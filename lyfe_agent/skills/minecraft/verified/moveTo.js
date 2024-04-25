/**
 * Moves the bot to a position relative to its own position and orientation.
 * 
 * @param {Object} bot - The Mineflayer bot instance.
 * @param {Vec3} relativePosition - The relative position to move to.
 * 
 * Example usage:
 * moveTo(bot, new Vec3(2, 1, 3));  // 2 right, 1 up, 3 forward
 */

function moveTo(bot, relativePosition) {
    // Calculate the bot's current forward and right vectors based on its yaw
    const yaw = bot.entity.yaw;
    const forward = new Vec3(-Math.sin(yaw), 0, -Math.cos(yaw));
    const right = new Vec3(forward.z, 0, -forward.x);

    // Calculate the target position
    const targetPosition = bot.entity.position.offset(
        forward.x * relativePosition.z + right.x * relativePosition.x,
        relativePosition.y,
        forward.z * relativePosition.z + right.z * relativePosition.x
    );

    // Use pathfinder to move to the target position
    bot.pathfinder.setGoal(new GoalBlock(targetPosition.x, targetPosition.y, targetPosition.z));
}
