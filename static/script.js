function fetchStockData() {
    let ticker = document.getElementById("stockTicker").value.toUpperCase();
    if (!ticker) {
        alert("Please enter a stock symbol!");
        return;
    }

    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("stockData").textContent = "";
    document.getElementById("marketNews").textContent = "";
    document.getElementById("analysisData").textContent = "";
    document.getElementById("recommendationData").textContent = "";

    fetch("/get_stock_data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker: ticker })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("loading").classList.add("hidden");

        document.getElementById("stockData").textContent = JSON.stringify(data.stock_data, null, 4);
        document.getElementById("marketNews").textContent = data.news;
        document.getElementById("analysisData").textContent = data.analysis;
        document.getElementById("recommendationData").textContent = data.recommendation;
    })
    .catch(error => {
        document.getElementById("loading").classList.add("hidden");
        alert("Error fetching stock data!");
        console.error(error);
    });
}