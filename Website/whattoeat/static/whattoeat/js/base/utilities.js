$(document).ready(function () {
            //round units to one decimal place for display
            function round_units() {
                var decimals = $('.rounded_decimal');
                for (i = 0; i < decimals.length; i++) {
                    var target = decimals[i];
                    var value = parseFloat(target.innerHTML);
                    value = Math.round(value * 10) / 10;
                    target.textContent = value;
                }
            }

            round_units();
});