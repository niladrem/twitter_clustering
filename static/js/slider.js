    var slider = document.getElementById("genie_th");
    var output = document.getElementById("val");
    output.innerHTML = slider.value;

    slider.oninput = function() {
      output.innerHTML = this.value;
    }