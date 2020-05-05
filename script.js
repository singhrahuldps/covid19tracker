

window.addEventListener('DOMContentLoaded', function(){
    var algoselect = document.querySelector('#algoselect');
    var countryselect = document.querySelector('#countryselect');
    var aboutalgo = document.querySelector('#aboutalgo');
    var frame = document.querySelector('#mapframe');

    
    document.querySelector('#setFrameHTML').addEventListener('click', function(){
        var algo = algoselect.options[algoselect.selectedIndex];
        var algoname = algo.value;
        var algodesc = algo.dataset.desc;
        var optgroup = algo.parentNode.label;

        aboutalgo.innerHTML = algodesc;

        var newHTML= 'charts/' + optgroup + '/' + algoname + '/' + countryselect.options[countryselect.selectedIndex].value + '.html';
        //var linkHTML = 'https://raw.githack.com/singhrahuldps/covid19tracker/master/charts/singhrahuldps/BestFitBellCurve/' + countryselect.options[countryselect.selectedIndex].value + '.html';
        //alert(linkHTML);
        //downloadURI(linkHTML, newHTML);
        frame.src = newHTML;
    });
});

