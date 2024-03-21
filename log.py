import logging

# Configure logging for authLog.txt
authLog = logging.getLogger('authLog')
authLog.setLevel(logging.INFO)
authHangler = logging.FileHandler('authLog.txt')
authHangler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
authLog.addHandler(authHangler)

# Configure logging for configChangesLog.txt
configChangeLog = logging.getLogger('configChangeLog')
configChangeLog.setLevel(logging.INFO)
configHandler = logging.FileHandler('configChangesLog.txt')
configHandler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
configChangeLog.addHandler(configHandler)

# Usage Example
# authLog.info('This is a message for auth_log.txt')
# configChangeLog.info('This is a message for config_Changes_Log.txt')
