import re
class Util:
    @staticmethod
    def y_or_n(input_answer):
        y = '^[yY][eE]{0,1}[sS]{0,1}$'
        n = '^[nN][oO]{0,1}$'
        if re.match(y, input_answer):
            return 'yes'
        elif re.match(n, input_answer):
            return 'no'
        else:
            return -1

    @staticmethod
    def human_readable_time(seconds):
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        sec = int(seconds % 60)
        milliseconds = int((seconds - int(seconds)) * 1000)

        if days > 0:
            return f"{int(days)}d {int(hours)}h, {int(minutes)}m, {int(seconds)}s, {milliseconds}ms"
        elif hours > 0:
            return f"{int(hours)}h, {int(minutes)}m, {int(seconds)}s, {milliseconds}ms"
        elif minutes > 0:
            return f"{int(minutes)}m, {int(seconds)}s, {milliseconds}ms"
        elif seconds > 0:
            return f"{sec} seconds, {milliseconds} milliseconds"
        else:
            return f"{milliseconds} milliseconds"