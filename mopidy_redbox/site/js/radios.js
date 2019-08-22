function openPage(pageName, elmnt, color) {
    // Hide all elements with class="tabcontent" by default */
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("radios-tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].className = "radios-tabcontent";
    }
    document.getElementById(pageName).className = "radios-tabcontent active";


    // Remove the background color of all tablinks/buttons
    tablinks = document.getElementsByClassName("radios-tablink");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = "radios-tablink";
    }
    // Add the specific color to the button used to open the tab content
    elmnt.className = "radios-tablink active";

    // update value of add radio button
    document.getElementById("radios-addradio-button").setAttribute("value", pageName); 

    //hide add radio form
    document.getElementById("radios-addradio").style.display = "none";
}

function addBank() {
    var bankList = document.getElementById("radios-banks");
    newBankDiv = document.createElement("div");

    var form = document.createElement("form");
    form.setAttribute('method',"post");
    form.setAttribute('action',"radios");

    var i = document.createElement("input"); //input element, text
    i.setAttribute('type',"text");
    i.setAttribute('name',"new_bank");
    form.appendChild(i);

    newBankDiv.appendChild(form);

    newBankDiv.className = "radios-new-bank";
    bankList.appendChild(newBankDiv);
}

function deleteBank(bank) {
    minus = document.getElementById("radio-tab-del-"+bank);
    minus.style.display = "none";

    tab = document.getElementById("radios-tab-" + bank);
    var form = document.createElement("form");
    form.setAttribute('method',"post");
    form.setAttribute('action',"radios");

    var i = document.createElement("button"); //input element, text
    i.setAttribute('type',"submit");
    i.setAttribute('name',"del_bank");
    i.setAttribute('value', bank);
    i.innerText = "Delete";
    form.appendChild(i);

    tab.appendChild(form);
}

function addRadio() {
    form = document.getElementById("radios-addradio");
    form.style.display = "block";
}

function deleteRadio(bank, radio) {
    entry = document.getElementById("delete-"+bank+"-"+radio);
    entry.style.width = "100px";
    var form = document.createElement("form");
    form.setAttribute('method',"post");
    form.setAttribute('action',"radios");

    var i = document.createElement("button"); //input element, text
    i.setAttribute('type',"submit");
    i.setAttribute('name',"del_radio");
    i.setAttribute('value', radio);
    i.innerText = "Delete";
    form.appendChild(i);

    entry.appendChild(form);

}