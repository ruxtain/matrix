$(function(){
    asin_urls = {
        'JP':'https://www.amazon.co.jp/dp/',
        'UK':'https://www.amazon.co.uk/dp/',
        'ES':'https://www.amazon.es/dp/',
        'FR':'https://www.amazon.fr/dp/',
        'US':'https://www.amazon.com/dp/',
        'IT':'https://www.amazon.it/dp/',
        'AU':'https://www.amazon.com.au/dp/',
        'DE':'https://www.amazon.de/dp/',
        'CA':'https://www.amazon.ca/dp/',
    } 
    search_urls = {
        'JP':'https://www.amazon.co.jp/s/field-keywords=',
        'UK':'https://www.amazon.co.uk/s/field-keywords=',
        'ES':'https://www.amazon.es/s/field-keywords=',
        'FR':'https://www.amazon.fr/s/field-keywords=',
        'US':'https://www.amazon.com/s/field-keywords=',
        'IT':'https://www.amazon.it/s/field-keywords=',
        'AU':'https://www.amazon.com.au/s/field-keywords=',
        'DE':'https://www.amazon.de/s/field-keywords=',
        'CA':'https://www.amazon.ca/s/field-keywords=',        
    }
    // *** 用于给不同国家的标签变色 ***
    $(".bodys p").not(":first").hide(); //除了第一个，其他的都隐藏
    $(".searchbox ul li").mouseover(function(){ // 悬停国别时
        var index = $(this).index();
        $(this).find("a").addClass("active");
        $(".searchbox ul li").each(function() {
            var index2=$(this).index();
            if (index2 != index) {
                $(this).find("a").removeClass("active");
            }
        })
        $(".bodys p").eq(index).show().siblings().hide();

    });

    // 只有当搜索框被激活时，回车才是搜索
    $("#searchbox").bind("focus", function() {
        // 因为keypress很容易检测到多次按键，于是造成多个弹窗。
        // 我用了一个flag，在打开一个标签后拒绝继续打开。
        // 此时调动了open，使搜索框失去聚焦，又回到初始状态，又可以继续弹窗。
        $(this).bind("keyup", function(e) {  
            if (e.keyCode == 13) {  
                linkGenerate();
                // 我不知道怎么从其他函数传参数 于是就直接用DOM作为中介来传递数据
                var link = $("#searchbutton").find("a").attr("href");
                window.open(link);
             }  
        });
        // 这里必须要unbind这个focus，不然每次失去焦点后又回到这里，它会启动次数加1
        // 回车第一次开一个网页，回车第二次就开两个网页了，以此类推，很可怕。
        $(this).unbind("focus");
    });

    $("#searchbutton").mouseover(function() {
        linkGenerate();
    });

    // 这部分用于处理bp的字数计算
    $(".bpInput").bind('input propertychange', function() {
        var content = $(this).val();
        var bpList0 = content.split("\n");
        // console.log(bpList0);
        var bpList = [];
        for (var i = 0; i < bpList0.length; i++) {
            if (bpList0[i] != "") {
                bpList.push(bpList0[i]);
            }
        };
        bp1 = bpList[0];
        bp2 = bpList[1];
        bp3 = bpList[2];
        bp4 = bpList[3];
        bp5 = bpList[4];
        try {
            $("#bpc1").html(bp1.length);
            $("#bpc2").html(bp2.length);
            $("#bpc3").html(bp3.length);
            $("#bpc4").html(bp4.length);
            $("#bpc5").html(bp5.length);
        } catch (err) {
            // console.log(err);
        };
        // 填写后又清空计数器会显示前两行是1，这里放个马后炮清除一下 具体原因不追究
        if (bpList.length == 0) {
            $(".bpc").each(function() { 
                $(this).html(0);
            });
        };
        
    });

    // 这部分处理search terms
    $(".stInput").bind('input propertychange', function() {
        var s = $(this).val().replace(/[\s\n\r]+/g, '').trim();
        var size = byteSize(s);
        $("#stc").html(size);
    });

   // 这部分处理复制内容的按钮
    $(".copyBtn").click(function() {
        var master = $("." + $(this).data("for"));
        var content = master.val();
        copyTextToClipboard(content);
        master.select();
    }); 

    // 为了提高编辑效率 快速情况框框
    $(".clearBtn").click(function() {
        var master = $("." + $(this).data("for"));
        master.val("");
    });



});   // 这个main域的边界，以上的部分才能运行，以下的部分只能被上面引用。  


function linkGenerate() {
    var k = $("#searchbox").val().trim();
    $(".searchbox ul li").each(function() {
        if ($(this).find("a").hasClass("active")) {
            var country = $(this).find("a").text();
            // console.log(country);
            // 确定了国别之后，进一步确定输入的是asin还是关键字
            if (/^B[A-Z0-9]{9}/g.test(k)) {
                var link = asin_urls[country] + k;
                $("#searchbutton").find("a").attr("href", link);
            }
            // 必须是非空才可以检索
            else if (/\S+/g.test(k)) {
                var link = search_urls[country] + k
                $("#searchbutton").find("a").attr("href", link);
            }
            
        }
    });
}

// 这个函数用的别人的 可以直接更改剪切板
function copyTextToClipboard(text) {
  var textArea = document.createElement("textarea");

  //
  // *** This styling is an extra step which is likely not required. ***
  //
  // Why is it here? To ensure:
  // 1. the element is able to have focus and selection.
  // 2. if element was to flash render it has minimal visual impact.
  // 3. less flakyness with selection and copying which **might** occur if
  //    the textarea element is not visible.
  //
  // The likelihood is the element won't even render, not even a flash,
  // so some of these are just precautions. However in IE the element
  // is visible whilst the popup box asking the user for permission for
  // the web page to copy to the clipboard.
  //

  // Place in top-left corner of screen regardless of scroll position.
  textArea.style.position = 'fixed';
  textArea.style.top = 0;
  textArea.style.left = 0;

  // Ensure it has a small width and height. Setting to 1px / 1em
  // doesn't work as this gives a negative w/h on some browsers.
  textArea.style.width = '2em';
  textArea.style.height = '2em';

  // We don't need padding, reducing the size if it does flash render.
  textArea.style.padding = 0;

  // Clean up any borders.
  textArea.style.border = 'none';
  textArea.style.outline = 'none';
  textArea.style.boxShadow = 'none';

  // Avoid flash of white box if rendered for any reason.
  textArea.style.background = 'transparent';


  textArea.value = text;

  document.body.appendChild(textArea);

  textArea.select();

  try {
    var successful = document.execCommand('copy');
    var msg = successful ? 'successful' : 'unsuccessful';
    console.log('Copying text command was ' + msg);
  } catch (err) {
    console.log('Oops, unable to copy');
  }

  document.body.removeChild(textArea);
}

// // 这部分用于处理bp
// var charCount = function(s){return s.length};
// var el = document.getElementById("bp1c");

// document.getElementById("bp1").oninput = function() {
//     var len = charCount(this.value);
//     el.innerHTML = len;
//     if (len > 100) {
//         el.style.color="red";
//     }
//     else {
//         el.style.color="black";
//     }
// };

function byteSize(s){return unescape(encodeURI(s)).length};
// var el = document.getElementById('stc');

// document.getElementById('stInput').oninput = function() {
//     pure = this.value.replace(/[\s\n\r]+/g, '').trim();
//     el.innerHTML = byteSize(pure);
// };