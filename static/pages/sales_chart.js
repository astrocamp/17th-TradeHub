document.addEventListener("DOMContentLoaded", function () {
  const canvas = document.getElementById("myPieChart");

  // 获取并解析 JSON 数据
  const productDataElement = document.getElementById("productData");
  const productData = JSON.parse(productDataElement.textContent);

  const products = productData.product; // 产品名称
  const quantities = productData.quantity; // 数量
  const colors = productData.color; // 颜色

  const ctx = canvas.getContext("2d");

  const myPieChart = new Chart(ctx, {
    type: "pie",
    data: {
      labels: products,
      datasets: [
        {
          label: "熱銷商品",
          data: quantities,
          backgroundColor: colors,
          borderColor: "white",
          borderWidth: 2,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
          position: "top",
        },
        tooltip: {
          callbacks: {
            label: function (tooltipItem) {
              let total = quantities.reduce((a, b) => a + b, 0);
              let percentage = ((tooltipItem.raw / total) * 100).toFixed(2);
              return `${tooltipItem.label}: ${percentage}%`;
            },
          },
        },
      },
    },
  });
});
