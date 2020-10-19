
function formatDollars(value) {
  return Number(value).toLocaleString("en-US", {style : "currency", currency: "USD"})
}

function formatMetric(value) {
  return Number(value).toPrecision(4)
}


let plotWidth = null
let plotHeight = null

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
  xhttp.send("row=" + row + "&col=" + col + "&width=" + plotWidth + "&height=" + plotHeight)
}


function fetchMetric(metoptwid) {
  const id = metoptwid.id.split("_")
  const row = id[1]
  let xhttp = new XMLHttpRequest()
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200)
      metoptwid.value = this.responseText
      document.getElementById(metoptwid.id.replace("wid", "lab")).innerText = "Current: " + formatMetric(this.responseText)
  };
  xhttp.open("POST", "/metric", true)
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhttp.send("row=" + row)
}


function postInvestment(col, value) {
  let xhttp = new XMLHttpRequest()
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      Array.from(document.getElementsByClassName("metoptwid")).forEach(fetchMetric)
      Array.from(document.getElementsByClassName("plot")).forEach(function(plot) {
        const id = plot.id.split("_")
        const col1 = id[2]
        if (col1 == col || col1 == "x")
          fetchPlot(plot)
      })
    }
  };
  xhttp.open("POST", "/invest", true)
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhttp.send( "col=" + col + "&value=" + value)
}


function updateInvestment(slider) {
  let value = slider.value
  let label = slider.id.replace("wid", "lab")
  document.getElementById(label).innerText = "Allowed: " + formatDollars(value)
  let meter = slider.id.replace("lim", "opt")
  document.getElementById(meter).value = value
  let label1 = slider.id.replace("limwid", "optlab")
  document.getElementById(label1).innerText = "Current: " + formatDollars(value)
  updateTotal()
  postInvestment(label.split("_")[1], value)
}


function updateTotal() {
  let investment = Array.from(document.getElementsByClassName("islider")).reduce(function(total, slide) {
    return total + parseInt(slide.value)
  }, 0)
  invoptlab_x.innerText = "Current: " + formatDollars(investment)
  invoptwid_x.value = investment
  invlimlab_x.innerText = "Allowed: " + formatDollars(investment)
  invlimwid_x.value = investment
}


function updateMetricLabel(target) {
  const value = document.getElementById(target.htmlFor).value
  target.innerText = target.innerText.split(" ")[0] + " "  + formatMetric(value)
}

function updateInvestLabel(target) {
  const value = document.getElementById(target.htmlFor).value
  target.innerText = target.innerText.split(" ")[0] + " "  + formatDollars(value)
}


function setup() {
  Array.from(document.getElementsByClassName("plot")).forEach(plot => fetchPlot(plot))
  Array.from(document.getElementsByClassName("metoptwid")).forEach(fetchMetric)
  Array.from(document.getElementsByClassName("metoptlab")).forEach(updateMetricLabel)
  Array.from(document.getElementsByClassName("metlimlab")).forEach(updateMetricLabel)
  Array.from(document.getElementsByClassName("invoptlab")).forEach(updateInvestLabel)
  Array.from(document.getElementsByClassName("invlimlab")).forEach(updateInvestLabel)
}
