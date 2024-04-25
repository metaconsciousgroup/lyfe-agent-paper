/**
 * Stops the bot from following any entity it was previously following.
 * 
 * @param {*} bot - The Mineflayer bot instance.
 * 
 * Example usage:
 * stopFollowing(bot);
 */
function stopFollowing(bot) {
    if (bot.pathfinder.goal) {
        bot.pathfinder.setGoal(null);
        bot.chat("Stopped following.");
    } else {
        bot.chat("I was not following anyone.");
    }

    // If you've added a 'physicTick' event listener for following, remove it here
    // TODO: unsure if this will work
    // bot.removeListener('physicTick', checkDistance);
}
