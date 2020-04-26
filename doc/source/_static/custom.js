
function choose_version(value){
    console.log("CHOOSE VERSION");
    console.log(value);

    console.log(window.location.href);
    var parts = window.location.href.split("/MetaWards/");
    console.log(parts);

    // should be two parts - before /MetaWards/ and after
    s = parts[0];
    s += "/MetaWards";
    s += value;

    if (parts[1].startsWith("versions/")){
        var parts2 = parts[1].split("/");
        parts2.shift();
        parts2.shift();
        parts[1] = parts2.join("/");
    }

    for (var i=1; i<parts.length - 1; ++i){
        s += parts[i] + "/MetaWards/";
    }

    s += parts[parts.length-1];

    console.log(`Redirecting to ${s}`);
    window.location = s;
}

function fill_versions(){
    var xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var versions = JSON.parse(this.responseText);
            console.log(versions)

            var s = "<div class=\"version_box\">" +
                    "<select id=\"versions\" onchange=\"choose_version(this.value)\">";

            for (var i in versions){
                var version = versions[i][0];
                var path = versions[i][1];
                s += `<option value="${path}">${version}</option>`;
            }

            s += "</select></div>";

            document.getElementById("version_box").innerHTML = s;
        }
    };

    xmlhttp.open("GET", "https://metawards.github.io/MetaWards/versions.json",
                 true);
    xmlhttp.send();
}

window.onload = fill_versions;
