import collections


class Stats:
    def split_camel_case(self, camel_case_string):
        words = [[camel_case_string[0]]]

        for c in camel_case_string[1:]:
            if words[-1][-1].islower() and c.isupper():
                words.append(list(c))
            else:
                words[-1].append(c)

        words = [''.join(word) for word in words]
        resulting_string = ' '.join(words).title()

        return resulting_string

    def sort_by_time_played(self, stats_dictionary):
        def get_time_played(current_hero):
            try:
                time_played = current_hero[1]['timePlayed']
                return time_played
            except KeyError:
                time_played = 0
                return time_played

        sorted_heroes_by_time_played = dict(collections.OrderedDict(
            sorted(
                stats_dictionary.items(),
                key=get_time_played,
                reverse=True
            )
        ))

        return sorted_heroes_by_time_played

    def get_stats_per_10(self, stats_list):
        hero_minutes_played = 0

        for stat in stats_list:
            try:
                if stat['name'] == 'Time Played':
                    hero_minutes_played = stat['value']

            except TypeError:
                continue

        print(hero_minutes_played)

        list_per_10 = []
        if hero_minutes_played == 0:
            return stats_list

        for stat in stats_list:
            try:
                stat_name = stat['name']
                stat_value = stat['value']
            except TypeError:
                continue

            if stat_name == 'Time Played':
                list_per_10.append(stat)
            else:
                stat_per_10 = round((stat_value / hero_minutes_played) * 10)
                stat['value'] = stat_per_10
                list_per_10.append(stat)

        return list_per_10

    def format_details(self, hero_name, stats_dictionary):
        stats_dictionary_keys = stats_dictionary.keys()

        stats_list = [None] * 12
        for key in stats_dictionary_keys:
            stat_name = self.split_camel_case(key)
            if stat_name == 'Hero Damage Done':
                stat_name = 'Damage Done'

            if stat_name == 'Time Played':
                stat_value = round(int(stats_dictionary[key]) / 60)
            else:
                stat_value = int(stats_dictionary[key])

            current_stat = {'name': stat_name, 'value': stat_value}

            if current_stat['name'] == 'Time Played':
                stats_list[0] = current_stat
            elif current_stat['name'] == 'Eliminations':
                stats_list[1] = current_stat
            elif current_stat['name'] == 'Final Blows':
                stats_list[2] = current_stat
            elif current_stat['name'] == 'Deaths':
                stats_list[3] = current_stat
            elif current_stat['name'] == 'Damage Done':
                stats_list[4] = current_stat
            elif current_stat['name'] == 'Healing Done':
                stats_list[5] = current_stat
            elif current_stat['name'] == 'Damage Taken':
                stats_list[6] = current_stat
            elif current_stat['name'] == 'Shots Hit':
                stats_list[7] = current_stat
            elif current_stat['name'] == 'Critical Hits':
                stats_list[8] = current_stat
            elif current_stat['name'] == 'Ults Used':
                stats_list[9] = current_stat
            elif current_stat['name'] == 'Time Spent On Fire':
                stats_list[10] = current_stat
            elif current_stat['name'] == 'Solo Kills':
                stats_list[11] = current_stat
            elif current_stat['name'] == 'Ults Earned':
                continue
            else:
                stats_list.append(current_stat)

        stats_list_per_10 = self.get_stats_per_10(stats_list)

        for stat in stats_list_per_10:
            try:
                if stat['name'] == 'Time Played' and stat['value'] > 1:
                    hero_details = (hero_name.title(), stats_list)

                    return hero_details
            except TypeError:
                continue
