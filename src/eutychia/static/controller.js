
function formatDollars(value) {
  return Number(value).toLocaleString("en-US", {style : "currency", currency: "USD"})
}

function formatMetric(value) {
  return Number(value).toPrecision(4)
}


let plotWidth = null
let plotHeight = null

function fetchPlot(target) {
  const id = target.id.split("_")
  const row = id[1]
  const col = id[2]
  if (plotWidth == null) {
    const bounds = target.parentElement.getBoundingClientRect()
    plotWidth  = bounds.width  - 5
    plotHeight = bounds.height - 5
  }
  const xhttp = new XMLHttpRequest()
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200)
      target.src = this.responseText
  }
  xhttp.open("POST", "/plot", true)
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhttp.send("row=" + row + "&col=" + col + "&width=" + plotWidth + "&height=" + plotHeight)
}


function fetchMetric(target) {
  const id = target.id.split("_")
  const row = id[1]
  const xhttp = new XMLHttpRequest()
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200)
      target.value = this.responseText
      document.getElementById(target.id.replace("wid", "lab")).innerText = "Current: " + formatMetric(this.responseText)
  }
  xhttp.open("POST", "/metric", true)
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhttp.send("row=" + row)
}


function postInvestment(col, value) {
  const xhttp = new XMLHttpRequest()
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
  }
  xhttp.open("POST", "/invest", true)
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhttp.send( "col=" + col + "&value=" + value)
}


function updateInvest(target) {
  const label = target.id.replace("wid", "lab")
  updateInvestLabel(document.getElementById(label))
  if (explore_mode.checked) {
    const value = target.value
    updateTotal(true)
    postInvestment(label.split("_")[1], value)
  }
}


function updateMetric(target) {
  updateMetricLabel(document.getElementById(target.id.replace("wid", "lab")))
}


function updateTotal(all) {
  const investment = Array.from(document.getElementsByClassName("invpart")).reduce(function(total, slide) {
    return total + parseInt(slide.value)
  }, 0)
  invoptwid_x.value = investment
  updateInvestLabel(invoptlab_x)
  if (all) {
    invlimwid_x.value = investment
    updateInvestLabel(invlimlab_x)
  }
}


function updateMetricLabel(target) {
  const value = document.getElementById(target.htmlFor).value
  target.innerText = target.innerText.split(" ")[0] + " "  + formatMetric(- Number(value))
}

function updateInvestLabel(target) {
  const value = document.getElementById(target.htmlFor).value
  target.innerText = target.innerText.split(" ")[0] + " "  + formatDollars(value)
}


function optimize() {
  const constraints = {
    metric : {}
  , invest : {}
  }
  Array.from(document.getElementsByClassName("invlimwid")).forEach(
    target => constraints.invest[target.id] = Number(target.value)
  )
  Array.from(document.getElementsByClassName("metlimwid")).forEach(
    target => constraints.metric[target.id] = Number(target.value)
  )
  const xhttp = new XMLHttpRequest()
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      const result = JSON.parse(this.responseText)
      for (const [key, value] of Object.entries(result.amount)) {
        const target = document.getElementById(key)
        target.value = value
        updateInvest(target)
        Array.from(document.getElementsByClassName("plot")).forEach(plot => fetchPlot(plot))
        Array.from(document.getElementsByClassName("metoptwid")).forEach(fetchMetric)
        Array.from(document.getElementsByClassName("metoptlab")).forEach(updateMetricLabel)
        Array.from(document.getElementsByClassName("invoptlab")).forEach(updateInvestLabel)
        updateTotal(false)
        document.body.style.cursor = "default"
      }
    }
  }
  xhttp.open("POST", "/optimize", true)
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
  xhttp.send("constraints=" + JSON.stringify(constraints))
  document.body.style.cursor = "wait"
}

function setup() {
  Array.from(document.getElementsByClassName("plot")).forEach(plot => fetchPlot(plot))
  Array.from(document.getElementsByClassName("metoptwid")).forEach(fetchMetric)
  Array.from(document.getElementsByClassName("metoptlab")).forEach(updateMetricLabel)
  Array.from(document.getElementsByClassName("metlimlab")).forEach(updateMetricLabel)
  Array.from(document.getElementsByClassName("invoptlab")).forEach(updateInvestLabel)
  Array.from(document.getElementsByClassName("invlimlab")).forEach(updateInvestLabel)
}
