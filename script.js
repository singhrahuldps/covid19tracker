window.addEventListener('DOMContentLoaded', function(){
    
    var countryselect = document.querySelector('#countryselect');
    var frame = document.querySelector('#mapframe');
    
    document.querySelector('#setFrameHTML').addEventListener('click', function(){
        var newHTML= 'charts/singhrahuldps/BestFitBellCurve/' + countryselect.options[countryselect.selectedIndex].value + '.html';
        //var linkHTML = 'https://raw.githack.com/singhrahuldps/covid19tracker/master/charts/singhrahuldps/BestFitBellCurve/' + countryselect.options[countryselect.selectedIndex].value + '.html';
        //alert(linkHTML);
        //downloadURI(linkHTML, newHTML);
        frame.src = newHTML;
    });
});

