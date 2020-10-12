
var plotWidth = null
var plotHeight = null

function fetchPlot(plot) {
  const id = plot.id.split("_")
  const row = id[1]
  const col = id[2]
  if (plotWidth == null) {
    const bounds = plot.parentElement.getBoundingClientRect()
    plotWidth  = bounds.width  - 5
    plotHeight = bounds.height - 5
  }
  let xhttp = new XMLHttpRequest()
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200)
      plot.src = this.responseText
  };
  xhttp.open("POST", "/plot", true)
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhttp.send( "row=" + row + "&col=" + col + "&width=" + plotWidth + "&height=" + plotHeight)
}


function postInvestment(col, value) {
  let xhttp = new XMLHttpRequest()
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200)
      Array.from(document.getElementsByClassName("plot")).forEach(function(plot) {
        const id = plot.id.split("_")
        const col1 = id[2]
        if (col1 == col || col1 == "x")
          fetchPlot(plot)
      })
  };
  xhttp.open("POST", "/invest", true)
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhttp.send( "col=" + col + "&value=" + value)
}


function updateInvestment(slider) {
  let value = slider.value
  let label = slider.id.replace("v", "t")
  document.getElementById(label).innerText = "$" + value
  updateTotal()
  postInvestment(label.split("_")[1], value)
}


function updateTotal() {
  let investment = Array.from(document.getElementsByClassName("slide")).reduce(function(total, slide) {
    return total + parseInt(slide.value)
  }, 0)
  int_x.innerText = "$" + investment
  inv_x.value = investment
}


function setup() {
  Array.from(document.getElementsByClassName("plot")).forEach(plot => fetchPlot(plot))
}
