/**
 * Created by michael on 14/01/14.
 */

grams_nutrients = ["PROTEIN","CARBS","FAT","SUGAR","SALT","SATFAT","FIBRE"]

function nutrient_unit(nutrientName){
    n = nutrientName.toUpperCase();
    if(n == "CALORIES"){
        return "kcal";
    }else if(grams_nutrients.contains(n)){
        return "g"
    }
    return "UNKNOWN UNIT"
}