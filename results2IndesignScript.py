import json

def generate_indesign_script():
    # Read the JSON file
    with open('output/final_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Generate the InDesign script
    script_lines = []
    script_lines.append("""function setText(doc, sentences, pageNum, left_ratio, top_ratio, right_ratio, bottom_ratio) {
    /*
    根据传入的参数，设置文字的位置。
    可自动调整单双页位置偏移。
    input:doc,sentences,pageNum,left_ratio,top_ratio,right_ratio,bottom_ratio
    output:/
    */
    var pageBounds = doc.pages[pageNum - 1].bounds;  // [top, left, bottom, right]
    var pageWidth = pageBounds[3] - pageBounds[1];
    var pageHeight = pageBounds[2] - pageBounds[0];
    
    var tf1 = doc.pages[pageNum - 1].textFrames.add();
    tf1.parentStory.storyPreferences.storyOrientation = StoryHorizontalOrVertical.VERTICAL;

    // 计算文本框的实际坐标
    var actualTop = pageBounds[0] + (pageHeight * top_ratio);
    var actualLeft = pageBounds[1] + (pageWidth * left_ratio);
    var actualBottom = pageBounds[0] + (pageHeight * bottom_ratio);
    var actualRight = pageBounds[1] + (pageWidth * right_ratio);
    
    tf1.geometricBounds = [actualTop, actualLeft, actualBottom, actualRight];
    
    //奇偶页判断，并移动位置。
    if (pageNum % 2 == 0) {
        //单数页不用操作
        tf1.move([doc.documentPreferences.pageWidth * (1 + left_ratio), doc.documentPreferences.pageHeight * top_ratio]);
    }
    else {
        //偶数页x坐标要加上页宽
        tf1.move([doc.documentPreferences.pageWidth * left_ratio, doc.documentPreferences.pageHeight * top_ratio]);
    }
    tf1.contents = sentences;
}

var doc = app.activeDocument;""")
    
    # Add setText calls for each entry in the JSON
    for item in data:
        sentences = item['transText'].replace('"', '\\"').replace('\n', '\\n')  # Escape quotes and newlines
        pageNum = item['pageNumber']
        left_ratio = item['x1Ratio']
        top_ratio = item['y1Ratio']
        right_ratio = item['x2Ratio']
        bottom_ratio = item['y2Ratio']
        
        script_line = f'setText(doc,"{sentences}",{pageNum},{left_ratio},{top_ratio},{right_ratio},{bottom_ratio})'
        script_lines.append(script_line)
    
    script_lines.append("// End of generated script")
    
    # Write the script to the output file
    with open('output/results2IndesignScript.jsx', 'w', encoding='utf-8') as f:
        f.write('\n'.join(script_lines))
    
    print("InDesign script generated successfully!")

if __name__ == "__main__":
    generate_indesign_script()