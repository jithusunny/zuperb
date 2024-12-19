function fuzzyTimePhrase() {
    const now = new Date();
    let hour = now.getHours();
    const minute = now.getMinutes();

    // Convert to 12-hour format
    const ampm = hour < 12 ? 'AM' : 'PM';
    hour = hour % 12;
    if (hour === 0) hour = 12; // midnight or noon

    // Decide on a fuzzy phrase based on the minute
    let phrase;
    if (minute < 15) {
        phrase = `Just after ${hour}`;
    } else if (minute < 30) {
        phrase = `Around quarter past ${hour}`;
    } else if (minute < 45) {
        phrase = `Around half past ${hour}`;
    } else if (minute < 60) {
        // Nearly next hour
        const nextHour = hour === 12 ? 1 : hour + 1;
        phrase = `Nearly quarter to ${nextHour}`;
    }

    // Add AM/PM for clarity, if desired
    phrase += ` ${ampm}`;

    return phrase;
}

function updateCurrentTime() {
    const fuzzyText = fuzzyTimePhrase();
    document.getElementById('current-time').textContent = fuzzyText;
}

document.addEventListener('DOMContentLoaded', () => {
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000 * 60); // Update every minute for fuzziness
});
