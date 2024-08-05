let chartHandle;

const formatter = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",

  // These options are needed to round to whole numbers if that's what you want.
  minimumFractionDigits: 0, // (this suffices for whole numbers, but will print 2500.10 as $2,500.1)
  maximumFractionDigits: 0, // (causes 2500.99 to be printed as $2,501)
});

// this is so kludgy; we should be operating on data not chart rows but so be it
function renderChart(tableData) {
  const plotData = [];

  // this isn't really doing a mapping because we get a bunch of constructor garbage from the node
  tableData.nodes().map((row) => {
    const property = JSON.parse(atob(row.getAttribute("data-property")));
    plotData.push({
      propertyID: property.property_id,
      x: property.sale_per_acre_delta_of_appraisal,
      y: property.dollars_per_acre,
    });
  });

  const config = {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Sale Price and Appraisal Delta",
          data: plotData,
        },
      ],
    },
    options: {
      scales: {
        x: {
          type: "logarithmic",
          position: "bottom",
        },
      },
      plugins: {
        tooltip: {
          callbacks: {
            label: function (context) {
              let label = context.dataset.label || "";

              if (label) {
                label += ": ";
              }

              if (context.raw.propertyID !== null) {
                label += context.raw.propertyID + " -- ";
              }

              if (context.parsed.x !== null) {
                label += context.parsed.x + "%, ";
              }

              if (context.parsed.y !== null) {
                label += new Intl.NumberFormat("en-US", {
                  style: "currency",
                  currency: "USD",
                }).format(context.parsed.y);
              }
              return label;
            },
          },
        },
      },
    },
  };

  const ctx = document.getElementById("askScatterPlot");
  if (chartHandle) {
    chartHandle.destroy();
  }
  chartHandle = new Chart(ctx, config);
}

function fetchAndRender(filterFunc) {
  fetch("./Klamath Forest Estates + First Addition Property Dump.json")
    .then((response) => response.json())
    .then(filterFunc)
    .then((data) =>
      data.map((property) => {
        const saleDate = new Date(0);
        saleDate.setUTCMilliseconds(property.SALE_DATE);
        const saleYear = saleDate.toISOString().split("T")[0];

        return {
          property_id: property.PROP_ID,
          sale_price: property.SALE_PRICE,
          sale_year: saleYear,
          acreage: property.ACREAGE,
          dollars_per_acre: Math.round(property.SALE_PRICE / property.ACREAGE),
          appraisal_price: property.LND_APPR,
          appraisal_dollars_per_acre: Math.round(
            property.LND_APPR / property.ACREAGE
          ),
          sale_per_acre_delta_of_appraisal: Math.round(
            (property.SALE_PRICE /
              property.ACREAGE /
              (property.LND_APPR / property.ACREAGE)) *
              100
          ),
          owner_name: property.OWNER_NAME,
          owner_state: property.MAILST,
          owner_city: property.MAILCITY,
          lat: property.INSIDE_Y,
          lon: property.INSIDE_X,
        };
      })
    )
    .then((data) => {
      document.querySelector("#dataTable").innerHTML += data
        .map(
          (property) =>
            `
               <tr data-property="${btoa(JSON.stringify(property))}">
                 <td><a href="https://assessor.klamathcounty.org/PSO/detail/${
                   property.property_id
                 }/R" target="_blank">${property.property_id}</a></td>
                 <td>${property.sale_year}</td>
                 <td><a href="https://www.google.com/maps/place/${
                   property.lat
                 },${property.lon}" target="_blank">${property.acreage}</a></td>
                 <td>${formatter.format(property.sale_price)}</td>
                 <td>${formatter.format(property.appraisal_price)}</td>
                 <td>${formatter.format(property.dollars_per_acre)}</td>
                 <td>${formatter.format(
                   property.appraisal_dollars_per_acre
                 )}</td>
                 <td>${property.sale_per_acre_delta_of_appraisal}%</td>
                 <td>${property.owner_name}</td>
                 <td>${property.owner_state} [${property.owner_city}]</td>
               </tr>`
        )
        .join("");
    })
    .then((data) => {
      $(document).ready(function () {
        const table = $("#dataTable").DataTable();

        // get search result and chart it
        table.on("search.dt", () => {
          renderChart(table.rows({ filter: "applied" }));
        });

        renderChart(table.rows());
      });
    });
}
