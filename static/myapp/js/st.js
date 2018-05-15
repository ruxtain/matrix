$(function(){
var url = window.location.href;

    $("#arrowBtn1").click(function() {
        var goo = $(".gooInput").val().toLowerCase().split('\n');
        var good = [];
        for (i in goo) {
            g = goo[i];
            if ($.inArray(g, good)==-1) {
                if (isMeaningful(g)) {
                    good.push(g);
                }
            }
        }
        $("#rawInput").val(good.join('\n'));
        scrollTo("#duplicate2");
    })

    // deal with search terms
    $(".stInput").bind('input propertychange change', function() {
        var s = $(this).val().replace(/\s+/g, '').trim();
        var size = byteSize(s);
        $("#stc").html(size);
    });
    // the box above need to count too for comparison
    $(".rawInput").bind('input propertychange change', function() {
        var s = $(this).val().replace(/\s+/g, '').trim();
        var size = byteSize(s);
        $("#rtc").html(size);
    });    

}); // everything ends here

function byteSize(s){return unescape(encodeURI(s)).length};

function isMeaningful(s) {
    var nonsense = ['amazon usa', 'amazim', 'amqzonuk', 'anazinuk', 'azonuk', 'smazonuk', 'amzo9n', 'ww amaz', 
    'a axon uk', 'amaz8n uk', 'anaz9n', 'aa on', 'amaz0', 'amozanuk', 'ama on co uk', 'am uk', 'amaz on uk', 
    'amzonusa', 'amzonusa', 's mazon', 'us website', 'azoncom', 'amazmazon', 'am a zon com', 'amaz om', 
    'ama model', 'amzo0n', 'amazncm', 'amizoncom', 'amasoncom', 'am on com', 'amazi', 'www', 'amazon', 
    'am mazon', 'amazo', 'amzoncom', 'azonma', 'am ozone', 'amamzon', 'am axon', 'amazon com ', 'amazaon usa', 
    'buy ', 'wwww', 'amaz9n', 'amjon', 'ama on com', 'amejone', 'websites', 'download', 'amaxo com', 'amjon', 
    'amaz comon', 'amaz0n', 'amazl', 'amozon', 's sxpm', 'wwwama', 'amazan usa', 'www am', 'www amaxo', 
    'www amazz', 'a0az6n', 'amazol', 'ama om', 'marketing', 'a ma zon com', 'http', 'amax9n', 'amajon', 'imazone', 
    'amazomcom', 'wwwamaz', 'amizone ', 'wwwa', 'a comazon', 'shopping', 'amazom usa', 'online', 'dkakwhs', 
    'a zonam ', 'amezon', 'anazo ', 'fvfpjy', 'wew ama', 'smazin', 'anaxon', 'azonam', 'a mazo m', 'a azln', 
    'shipping ', 'good', 'cheap ', 'sale', 'price ', 'discount', 'shop', 'best', 'reviews ', 'deals ', 'am comazon', 
    'amaz0m', 'am zon com', 'amaoncom'];
    for (i in nonsense) {
        if (s.indexOf(nonsense[i]) >= 0) {
            return false; // contains nonsense, then s is not meaningful
        }
    }
    for (j in s) {
        if (s[j].charCodeAt() > 688) { // non-latin for sure
            return false;
        }        
    }
    return true;
}

// the functions bellow are idle for now


function getSelectedText() {
    return window.getSelection().toString().trim();
}












