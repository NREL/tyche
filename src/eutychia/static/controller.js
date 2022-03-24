

// Navigating elements.

function x2y(target, x, y) {
    return document.getElementById(target.id.replace(x, y))
  }
  
  function wid2lab(target) {
    return x2y(target, "wid", "lab")
  }
  
  function lab2wid(target) {
    return x2y(target, "lab", "wid")
  }
  
  function lim2opt(target) {
    return x2y(target, "lim", "opt")
  }
  
  function value4lab(target) {
    return document.getElementById(target.htmlFor).value
  }
  
  function forEachByClassName(clazz, action) {
    Array.from(document.getElementsByClassName(clazz)).forEach(action)
  }
  
  function reduceByClassName(clazz, action, initial) {
    return Array.from(document.getElementsByClassName(clazz)).reduce(action, initial)
  }
  
  
  // Extracting indices.
  
  function metcat(target) {
    const result = target.id.split("_")
    result.shift()
    return result
  }
  
  
  // Formatting numbers.
  
  function formatDollars(value) {
    return Number(value).toLocaleString("en-US", {style : "currency", currency: "USD"})
  }
  
  function formatMetric(value) {
    return Number(value).toPrecision(3)
  }
  
  
  // HTTP requests.
  
  function postRequest(path, parameters, action) {
    const xhttp = new XMLHttpRequest()
    xhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200)
        action(this.responseText)
    }
    xhttp.open("POST", path, true)
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
    xhttp.send(parameters)
  }
  
  
  // Fetching plots.
  
  let plotWidth = null
  let plotHeight = null
  
  function fetchPlot(target) {
    const [met, cat] = metcat(target)

    // [to-do] 1/# of rows. It will absolutely be greater than three.
    vscale = cat=="xall" ? 0.33 : 1

    if (plotWidth == null) {
      const bounds = target.parentElement.getBoundingClientRect()
      plotWidth  = bounds.width  - 0
      plotHeight = bounds.height - 0
    }
    plotType = plot_type.value
    postRequest(
      "/plot"
    , "met=" + met + "&cat=" + cat + "&width=" + plotWidth + "&height=" + (vscale*plotHeight) + "&plottype=" + plotType
    , function(responseText) {
        target.src = responseText
      }
    )
  }
  
  
  // Change in metric.
  
  function updateMetricLabel(target) {
    const value = value4lab(target)
    target.innerText = target.innerText.split(" ")[0] + " "  + formatMetric(- Number(value))
  }
  
  function updateMetric(target) {
    updateMetricLabel(wid2lab(target))
  }
  
  function fetchMetric(target) {
    const [met] = metcat(target)
    postRequest(
      "/metric"
    , "met=" + met
    , function(responseText) {
        target.value = responseText
        updateMetricLabel(wid2lab(target))
      }
    )
  }
  

  
  // Explore investments.
  
  function updateTotal(all) {
    const investment = reduceByClassName("invpart", function(total, slide) {
      return total + parseInt(slide.value)
    }, 0)
    invoptwid_x.value = investment
    updateInvestLabel(invoptlab_x)
    if (all) {
      invlimwid_x.value = investment
      updateInvestLabel(invlimlab_x)
    }
  }
  
  function updateInvestLabel(target) {
    const value = value4lab(target)
    target.innerText = target.innerText.split(" ")[0] + " " + formatDollars(value)
  }
  
  function syncInvest(target) {
    const value = target.value
    const target1 = lim2opt(target)
    target1.value = target.value
    updateInvestLabel(wid2lab(target1))
  }
  
  function updateInvest(target) {
    updateInvestLabel(wid2lab(target))
    if (explore_mode.checked) {
      syncInvest(target)
      updateTotal(true)
      postInvestment(metcat(target)[0], target.value)
    }
  }
  
  function postInvestment(cat, value) {
    postRequest(
      "/invest"
    , "cat=" + cat + "&value=" + value
    , function(responseText) {
        forEachByClassName("metoptwid", fetchMetric)
        forEachByClassName("plot", function(plot) {
          const [met1, cat1] = metcat(plot)
          if (cat1 == cat || cat1 == "x")
            fetchPlot(plot)
        })
      }
    )
  }
  
  
  function updateAllPlots() {
    forEachByClassName("plot", plot => fetchPlot(plot))
  }


  // Optimize investments.
  


  function updateResults(all) {
    updateAllPlots()
    forEachByClassName("metoptwid", fetchMetric)
    forEachByClassName("metoptlab", updateMetricLabel)
    forEachByClassName("invoptlab", updateInvestLabel)
    updateTotal(all)
  }
  
  function optimize() {
    const constraints = {
      metric : {}
    , invest : {}
    }
    forEachByClassName("invlimwid", target => constraints.invest[target.id] = Number(target.value))
    forEachByClassName("metlimwid", target => constraints.metric[target.id] = - Number(target.value))
    postRequest(
      "/optimize"
    , "target=" +  optimize_metric.value + "&constraints=" + JSON.stringify(constraints)
    , function(responseText) {
        const result = JSON.parse(responseText)
        optimizing_status.innerText = "Result: "
        optimizing_result.innerText = result.message
        for (const [key, value] of Object.entries(result.amount)) {
          const target = document.getElementById(key)
          target.value = value
          updateInvest(target)
        }
        updateResults(false)
        optimizing.style.cursor = "default"
        optimizing_close.disabled = false
      }
    )
    optimizing.style.display = "block"
  }
  
  function closeOptimizing() {
    optimizing.style.display = "none"
    optimizing_status.innerText = "Optimizing . . ."
    optimizing_result.innerText = ""
    optimizing_close.disabled = true
  }
  
  
  // Update mode.
  
  function updateMode() {
    const explorable = explore_mode.checked
    optimize_button.disabled = explorable
    optimize_metric.disabled = explorable
    invlimwid_x.disabled = explorable
    forEachByClassName("metlimwid", target => target.disabled = explorable)
    if (explorable) {
      forEachByClassName("invlimwid", syncInvest)
      updateTotal(true)
    }
  }
  
  
  // Setup.
  
  function setup() {
    forEachByClassName("metlimlab", updateMetricLabel)
    forEachByClassName("invlimlab", updateInvestLabel)
    updateResults(true)
  }
  
