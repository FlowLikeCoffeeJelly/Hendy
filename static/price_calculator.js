$(document).ready(function () {
    function calculateGrandTotal() {
        var grandTotal = 0;
        $(".quantity").each(function () {
            var quantity = parseInt($(this).text()) || 0; // use a default value of 0 if the quantity is not a valid integer
            var itemId = $(this).closest("tr").data("item-id");
            var price = parseFloat($(this).closest("tr").find("td:nth-child(2)").text()); // retrieve price from the same row
            grandTotal += price * quantity;
        });
        $("#grand-total").text("$" + grandTotal.toFixed(2));
    }

    $(".increment").click(function () {
        var quantityCell = $(this).closest("tr").find(".quantity"); // find the quantity cell in the same row
        var quantity = parseInt(quantityCell.text()) || 0;
        quantityCell.text(quantity + 1);
        calculateGrandTotal();
    });

    $(".decrement").click(function () {
        var quantityCell = $(this).closest("tr").find(".quantity");
        var quantity = parseInt(quantityCell.text()) || 0;
        if (quantity > 0) {
            quantityCell.text(quantity - 1);
            calculateGrandTotal();
        }
    });

    $(".incremend").click(function () {
        var quantityCell = $(this).closest("tr").find(".quantity");
        var quantity = parseInt(quantityCell.text()) || 0;
        quantityCell.text(quantity + 64);
        calculateGrandTotal();
    });

    $(".decremend").click(function () {
        var quantityCell = $(this).closest("tr").find(".quantity");
        var quantity = parseInt(quantityCell.text()) || 0;
        if (quantity >= 64) {
            quantityCell.text(quantity - 64);
            calculateGrandTotal();
        }
    });
});
