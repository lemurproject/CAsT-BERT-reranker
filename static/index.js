var G_startTime;
var G_endTime;
var G_activeSearchBar = "#searchbar_hero";
var G_inactiveSearchBar = "#searchbar_top";
var G_refresh = false;
var G_formattedResults = [];

function triggerSearch() {
    let searchQuery = $(G_activeSearchBar).val();
    if (searchQuery == "") {
        return;
    }
    let url = "search";
    console.log(searchQuery);
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify({'q': searchQuery}),
        success: handleResults
    });
    $('#search_btn_top').text("Searching...");
    $('#search_btn_hero').text("Searching...");
    $('#search_btn_top').removeClass("animate__pulse");
    $('#search_btn_hero').removeClass("animate__pulse");
    $('#search_btn_top').addClass("animate__pulse");
    $('#search_btn_hero').addClass("animate__pulse");
}

$.fn.digits = function(){
    return this.each(function(){
        $(this).text( $(this).text().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1,") );
    })
}

// {
//     "version": "1.0",
//     "timestamp": time_now,
//     "query": query,
//     "trec_eval_ranking", "1 Q0 " + doc_id + " " + rank + " " + score + " WEB_RANKING"
// }


function handleResults(results) {
    G_formattedResults = [];
    $('#search_btn_top').text("Search");
    $('#search_btn_hero').text("Search");
    $(G_inactiveSearchBar).val($(G_activeSearchBar).val());
    G_activeSearchBar = "#searchbar_top";
    G_inactiveSearchBar = "#searchbar_hero";
    $('.header').addClass('animate__backOutUp animate__faster');
    console.log(results.response);
    $('.flaunt #results_num').text(results.response.numFound.toLocaleString("en"));
    $('.flaunt #results_time').text(Math.round(results.queryDuration * 100) / 100);
    $('.pages').html('');
    //let date = new Date();
    //let timestamp = date.getTime();
    let date = Number(new Date());
    let time = new Date(date).toTimeString();
    let hdate = new Date(date).toDateString();
    let timestamp = hdate + " " + time
    $(results.response.docs).each(function(i, v) {
        console.log(i, v);
        let curr = '\
            <li>\
                <div class="page_title">\
                    '+v.fulltext[0].split(/\s+/).slice(0,15).join(" ") + "..."+'\
                </div>\
                <div class="page_docid">\
                    ID: '+v.id+'\
                </div>\
                <div class="page_content">\
                    '+v.fulltext[0]+'\
                </div>\
            </li>\
        ';
        G_formattedResults.push({
            "version": "1.0",
            "timestamp": timestamp,
            "query": $(G_activeSearchBar).val(),
            "trec_eval_ranking": "1 Q0 " + v.id + " " + (i + 1) + " " + v.score + " WEB_RANKING"
        });
        $('.pages').append(curr);
    });
    document.querySelector('.header').addEventListener('animationend', function() {
        $('.header').hide();
        $('.header_top').addClass('animate__backInDown');
        $('.header_top').show();
        $('.results').addClass('animate__backInUp');
        $('.results').show();
    });
}

function triggerDownload(extension, content) {
    let date = new Date();
    let timestamp = date.getTime();
    let filename = $(G_activeSearchBar).val() + "_" + timestamp + extension;
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

function triggerDownloadCSV() {
    let csv_content = Papa.unparse(G_formattedResults, {
        quotes: false, //or array of booleans
        quoteChar: '"',
        escapeChar: '"',
        delimiter: ",",
        header: true,
        newline: "\n",
        skipEmptyLines: true, //or 'greedy',
        columns: null //or array of strings
    });
    triggerDownload('.csv', csv_content);
}

function triggerDownloadJSON() {
    triggerDownload('.json', JSON.stringify(G_formattedResults));
}

$(document).ready(function() {
    $('#search_btn_hero').click(triggerSearch);
    $('#search_btn_top').click(triggerSearch);
    $('#download_csv_btn_top').click(triggerDownloadCSV);
    $('#download_json_btn_top').click(triggerDownloadJSON);
    $('.searchbar').keypress(function(e){
        if (e.which == 13) {
            triggerSearch();
        }
    });
    $('#about_btn').click(function() {
        if (G_refresh) {
            location.reload();
        }
        G_refresh = true;
        $('.header').addClass('animate__backOutUp animate__faster');
        $('.header_top').addClass('animate__backOutUp animate__faster');
        let url = "about";
        $.ajax({
            type: "GET",
            url: url,
            success: function(data) {
                $('.results').html(data);
            }
        });
        document.querySelector('.header').addEventListener('animationend', function() {
            $('.header').hide();
            $('.results').addClass('animate__backInUp');
            $('.results').show();
            $('#about_btn').text("Back");
        });
    });
});
