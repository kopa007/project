document.addEventListener("DOMContentLoaded", function() {
    const categoryNames = [];
    const categoryAmounts = [];

    // Loop over transactions in template to calculate total per category
    const transactions = {{ transactions|tojson }};
    const totals = {};

    transactions.forEach(t => {
        if (t.type === "expense") {
            if (!totals[t.category]) {
                totals[t.category] = 0;
            }
            totals[t.category] += t.amount;
        }
    });

    for (const [cat, amt] of Object.entries(totals)) {
        categoryNames.push(cat);
        categoryAmounts.push(amt);
    }

    // Create chart
    const ctx = document.getElementById("expenseChart").getContext("2d");
    const expenseChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: categoryNames,
            datasets: [{
                label: "Expenses by Category",
                data: categoryAmounts,
                backgroundColor: "rgba(75, 192, 192, 0.6)",
                borderColor: "rgba(75, 192, 192, 1)",
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
