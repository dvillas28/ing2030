// funcion para crear los graficos mas rapido
function createChart(elementId, datasetlabels, datasetData, titleLabel, xLabel, yLabel, color) {
    // para cargar los json
    var labels = JSON.parse(datasetlabels);
    var data = JSON.parse(datasetData);
    console.log(labels)
    console.log(data)

    // Your data for line chart
    var lineData = {
        labels: labels,
        datasets: [{
            label: titleLabel,
            data: data,
            borderColor: color, // Color of the line
            backgroundColor: 'rgba(255, 99, 132, 0.2)', // Color of the area under the line
            borderWidth: 1, // Width of the line
            fill: false // Fill the area under the line
        }]
    };

    // Create the line chart
    var ctx = document.getElementById(elementId).getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'line',
        data: lineData,

        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: xLabel
                    }
                },

                y: {
                    title: {
                        display: true,
                        text: yLabel
                    },

                    ticks: {
                        beginAtZero: true
                    },
                }
            }
        }
    });
}

// funcion para crear los graficos pastel
function createPieChart(elementId, datasetLabel1, datasetlabel2, title, color1, color2, data1, data2) {
    var ctx = document.getElementById(elementId).getContext('2d');
    var myChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: [datasetLabel1, datasetlabel2],
            datasets: [{
                data: [data1, data2],

                backgroundColor: [
                    color1,
                    color2
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)'
                ],
                borderWidth: 1
            }]
        },
        title: {
            display: true,
            text: title
        }
    });
}
