var setHTMLButton = document.getElementById('setHtml');

function setHTML(){
    var countryselect = document.getElementById('countryselect');
    var frame = document.getElementById('mapframe');
    var newHTML= 'charts/singhrahuldps/BestFitBellCurve/' + countryselect.options[countryselect.selectedIndex].value + '.html';
    frame.src = newHTML;
}

setHTMLButton.onclick(setHTML());