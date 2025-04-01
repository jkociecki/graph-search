
document.addEventListener("DOMContentLoaded", function () {
  let charts = {
    visitedConnectionsChart: null,
    numberOfTransfersChart: null,
    radarChart: null,
    horizontalBarChart: null,
  };

  const heuristics = [
    "Angle Between",
    "Euclidean Distance",
    "Haversine Changes",
    "Haversine Distance",
    "Zero Heuristic",
  ];
  const visitedConnections = [
    481.037383, 687.515439, 468.19863, 755.247191, 1243.934579,
  ];
  const transfers = [2.831776, 3.745843, 1.917808, 4.196629, 3.345794];
  const totalTime = [75.744444, 105.517857, 274.576642, 90.848921, 78.515306];

  const chartColors = {
    primary: "rgba(59, 130, 246, 0.7)", // Kolor główny
    primaryBorder: "rgba(59, 130, 246, 1)",
    secondary: "rgba(79, 70, 229, 0.7)", // Kolor dodatkowy
    secondaryBorder: "rgba(79, 70, 229, 1)",
    accent: "rgba(239, 68, 68, 0.7)", // Kolor akcentujący
    accentBorder: "rgba(239, 68, 68, 1)",
    success: "rgba(16, 185, 129, 0.7)", // Kolor sukcesu
    successBorder: "rgba(16, 185, 129, 1)",
    warning: "rgba(245, 158, 11, 0.7)", // Kolor ostrzeżenia
    warningBorder: "rgba(245, 158, 11, 1)",
  };

  // Wspólne opcje dla wszystkich wykresów
  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 1200,
      easing: "easeOutQuart",
    },
    plugins: {
      legend: {
        labels: {
          font: {
            family: "'Inter', sans-serif",
            size: 12,
          },
          color: "#495057",
        },
      },
      tooltip: {
        backgroundColor: "rgba(255, 255, 255, 0.9)",
        titleColor: "#212529",
        bodyColor: "#495057",
        borderColor: "#e9ecef",
        borderWidth: 1,
        padding: 12,
        boxPadding: 6,
        titleFont: {
          family: "'Inter', sans-serif",
          size: 14,
          weight: "bold",
        },
        bodyFont: {
          family: "'Inter', sans-serif",
          size: 13,
        },
        displayColors: true,
        usePointStyle: true,
      },
    },
  };

  function createOrUpdateCharts() {
    createVisitedConnectionsChart();

    createNumberOfTransfersChart();

    createRadarChart();

    createHorizontalBarChart();
  }

  // Wykres odwiedzonych połączeń
  function createVisitedConnectionsChart() {
    const ctx = document.getElementById("visitedConnectionsChart");
    if (!ctx) return;

    // Zniszcz istniejący wykres, jeśli istnieje
    if (charts.visitedConnectionsChart) {
      charts.visitedConnectionsChart.destroy();
    }

    charts.visitedConnectionsChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: heuristics,
        datasets: [
          {
            label: "Liczba odwiedzonych połączeń",
            data: visitedConnections,
            backgroundColor: chartColors.primary,
            borderColor: chartColors.primaryBorder,
            borderWidth: 1,
            borderRadius: 4,
            barPercentage: 0.7,
          },
        ],
      },
      options: {
        ...commonOptions,
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
            ticks: {
              font: {
                family: "'Inter', sans-serif",
                size: 11,
              },
              color: "#666",
            },
          },
          x: {
            grid: {
              display: false,
            },
            ticks: {
              font: {
                family: "'Inter', sans-serif",
                size: 11,
              },
              color: "#666",
            },
          },
        },
        plugins: {
          ...commonOptions.plugins,
          title: {
            display: false,
            text: "Liczba odwiedzonych połączeń",
            font: {
              family: "'Inter', sans-serif",
              size: 16,
              weight: "bold",
            },
            color: "#333",
            padding: {
              top: 10,
              bottom: 20,
            },
          },
        },
      },
    });
  }

  // Wykres liczby przesiadek
  function createNumberOfTransfersChart() {
    const ctx = document.getElementById("numberOfTransfersChart");
    if (!ctx) return;

    if (charts.numberOfTransfersChart) {
      charts.numberOfTransfersChart.destroy();
    }

    charts.numberOfTransfersChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: heuristics,
        datasets: [
          {
            label: "Średnia liczba przesiadek",
            data: transfers,
            backgroundColor: chartColors.warning,
            borderColor: chartColors.warningBorder,
            borderWidth: 1,
            borderRadius: 4,
            barPercentage: 0.7,
          },
        ],
      },
      options: {
        ...commonOptions,
        scales: {
          y: {
            beginAtZero: true,
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
            ticks: {
              font: {
                family: "'Inter', sans-serif",
                size: 11,
              },
              color: "#666",
            },
          },
          x: {
            grid: {
              display: false,
            },
            ticks: {
              font: {
                family: "'Inter', sans-serif",
                size: 11,
              },
              color: "#666",
            },
          },
        },
      },
    });
  }

  // Wykres radarowy wskaźników efektywności
  function createRadarChart() {
    const ctx = document.getElementById("radarChart");
    if (!ctx) return;

    if (charts.radarChart) {
      charts.radarChart.destroy();
    }

    charts.radarChart = new Chart(ctx, {
      type: "radar",
      data: {
        labels: [
          "Szybkość",
          "Wydajność",
          "Niezawodność",
          "Dokładność",
          "Komfort",
        ],
        datasets: [
          {
            label: "Angle Between",
            data: [85, 72, 90, 78, 82],
            fill: true,
            backgroundColor: "rgba(59, 130, 246, 0.2)",
            borderColor: "rgba(59, 130, 246, 0.8)",
            pointBackgroundColor: "rgba(59, 130, 246, 1)",
            pointBorderColor: "#fff",
            pointHoverBackgroundColor: "#fff",
            pointHoverBorderColor: "rgba(59, 130, 246, 1)",
          },
          {
            label: "Haversine",
            data: [65, 85, 74, 92, 67],
            fill: true,
            backgroundColor: "rgba(239, 68, 68, 0.2)",
            borderColor: "rgba(239, 68, 68, 0.8)",
            pointBackgroundColor: "rgba(239, 68, 68, 1)",
            pointBorderColor: "#fff",
            pointHoverBackgroundColor: "#fff",
            pointHoverBorderColor: "rgba(239, 68, 68, 1)",
          },
        ],
      },
      options: {
        ...commonOptions,
        scales: {
          r: {
            angleLines: {
              color: "rgba(0, 0, 0, 0.1)",
            },
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
            pointLabels: {
              font: {
                family: "'Inter', sans-serif",
                size: 12,
              },
              color: "#495057",
            },
            ticks: {
              backdropColor: "transparent",
              font: {
                size: 10,
              },
              color: "#666",
            },
          },
        },
      },
    });
  }

  // Wykres poziomy porównania przewoźników
  function createHorizontalBarChart() {
    const ctx = document.getElementById("horizontalBarChart");
    if (!ctx) return;

    if (charts.horizontalBarChart) {
      charts.horizontalBarChart.destroy();
    }

    charts.horizontalBarChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["PKP IC", "Polregio", "FlixBus", "ŁKA", "MPK"],
        datasets: [
          {
            label: "Zadowolenie klientów",
            data: [82, 74, 88, 76, 69],
            backgroundColor: chartColors.primary,
            borderColor: chartColors.primaryBorder,
            borderWidth: 1,
            borderRadius: 4,
            barPercentage: 0.8,
          },
          {
            label: "Punktualność",
            data: [68, 76, 80, 86, 72],
            backgroundColor: chartColors.accent,
            borderColor: chartColors.accentBorder,
            borderWidth: 1,
            borderRadius: 4,
            barPercentage: 0.8,
          },
          {
            label: "Stosunek jakości do ceny",
            data: [75, 82, 70, 78, 86],
            backgroundColor: chartColors.success,
            borderColor: chartColors.successBorder,
            borderWidth: 1,
            borderRadius: 4,
            barPercentage: 0.8,
          },
        ],
      },
      options: {
        ...commonOptions,
        indexAxis: "y",
        scales: {
          x: {
            beginAtZero: true,
            max: 100,
            grid: {
              color: "rgba(0, 0, 0, 0.05)",
            },
            ticks: {
              font: {
                family: "'Inter', sans-serif",
                size: 11,
              },
              color: "#666",
            },
          },
          y: {
            grid: {
              display: false,
            },
            ticks: {
              font: {
                family: "'Inter', sans-serif",
                size: 12,
                weight: "medium",
              },
              color: "#495057",
            },
          },
        },
      },
    });
  }

  createOrUpdateCharts();

  const chartCarousel = document.getElementById("ChartCarousel");
  if (chartCarousel) {
    chartCarousel.addEventListener("slide.bs.carousel", function (e) {
      setTimeout(createOrUpdateCharts, 100);
    });
  }

  window.addEventListener("resize", function () {
    setTimeout(createOrUpdateCharts, 200);
  });
});
