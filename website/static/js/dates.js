function getOrdinal(d) {
    if (d > 3 && d < 21) return "th";
    switch (d % 10) {
        case 1: return "st";
        case 2: return "nd";
        case 3: return "rd";
        default: return "th";
    }
}


function getMonthName(d) {
    switch (d) {
        case 1: return "January";
        case 2: return "February";
        case 3: return "March";
        case 4: return "April";
        case 5: return "May";
        case 6: return "June";
        case 7: return "July";
        case 8: return "August";
        case 9: return "September";
        case 10: return "October";
        case 11: return "November";
        case 12: return "December";
    }
    throw "Invalid date";
}


function getDateString(d) {
    d = new Date(d);
    ord = getOrdinal(d.getUTCDate());
    mon = getMonthName(d.getUTCMonth() + 1);
    return `${d.getUTCDate()}${ord} ${mon} ${d.getYear() + 1900}`
}
