$(function(){

var url = window.location.href;

    // 这部分用于处理bp的字数计算 
    $(".bpInput").bind("propertychange change keyup paste input", function() {
        var content = $(this).val().trim();
        var bpListWithEmptyLines = content.split("\n");
        // console.log(bpList);
        var bpList = [];
        for (i in bpListWithEmptyLines) {
            if (/\S+/g.test(bpListWithEmptyLines[i])){
                bpList.push(bpListWithEmptyLines[i]);
            }
        }
        for (i=0; i<5; i++) {
            var counter = $("#bpc" + (i+1).toString());
            if (bpList[i] == undefined) {
                var len = 0;
            } else {
                var len = bpList[i].length;
                // for hightlight bp exceeding the limit
                if (len > 500) {
                    counter.addClass('red');
                } else {
                    counter.removeClass('red');
                }
            }
            counter.html(len);
        }
        
    });
}) // the end of everything