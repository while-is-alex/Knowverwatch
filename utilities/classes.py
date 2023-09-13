class Stats:
    def split_camel_case(self, camel_case_string):
        words = []

        current_word = camel_case_string[0]
        for character in camel_case_string[1:]:
            if current_word[-1].islower() and character.isupper():
                words.append(current_word)
                current_word = character
            else:
                current_word += character

        words.append(current_word)
        resulting_string = ' '.join(words).title()

        return resulting_string

    def sort_by_name(self, stats_dictionary):
        heroes_sorted_by_name = dict(sorted(stats_dictionary.items()))

        return heroes_sorted_by_name

    def sort_by_time_played(self, stats_dictionary):
        def get_time_played(current_hero):
            return current_hero[1].get('timePlayed', 0)

        heroes_sorted_by_time_played = dict(
            sorted(
                stats_dictionary.items(),
                key=lambda x: get_time_played(x),
                reverse=True,
            )
        )

        return heroes_sorted_by_time_played

    def get_stats_per_10(self, stats_list):
        hero_minutes_played = 0

        for stat in stats_list:
            if stat['name'] == 'Time Played':
                hero_minutes_played = stat['value']

        if hero_minutes_played == 0:
            return stats_list

        list_of_stats_per_10 = []
        for stat in stats_list:
            stat_name = stat['name']
            stat_value = stat['value']

            if stat_name == 'Time Played':
                list_of_stats_per_10.append(stat)
            else:
                if stat_name in [
                    'Damage Done',
                    'Damage Taken',
                    'Shots Hit',
                    'Time Spent On Fire',
                ]:
                    stat_per_10 = round((stat_value / hero_minutes_played) * 10)
                else:
                    stat_per_10 = round((stat_value / hero_minutes_played) * 10, 2)

                stat['value'] = stat_per_10
                list_of_stats_per_10.append(stat)

        return list_of_stats_per_10

    def format_details(self, hero_name, stats_dictionary):
        stats_dictionary_keys = stats_dictionary.keys()

        stat_order = [
            'Time Played',
            'Eliminations',
            'Final Blows',
            'Deaths',
            'Damage Done',
            'Healing Done',
            'Damage Taken',
            'Shots Hit',
            'Critical Hits',
            'Ults Earned',
            'Ults Used',
            'Time Spent On Fire',
            'Solo Kills',
        ]

        stats_list = []
        for key in stats_dictionary_keys:
            stat_name = self.split_camel_case(key)

            if stat_name == 'Hero Damage Done':
                stat_name = 'Damage Done'

            stat_value = round((stats_dictionary[key]), 2)
            if stat_name == 'Time Played':
                stat_value = round(int(stats_dictionary[key]) / 60)  # seconds to minutes

            current_stat = {
                'name': stat_name,
                'value': stat_value,
            }

            if stat_name in stat_order:
                index = stat_order.index(stat_name)
                stats_list.insert(index, current_stat)
            else:
                stats_list.append(current_stat)

        stats_list_per_10 = self.get_stats_per_10(stats_list)

        for stat in stats_list_per_10:
            if stat['name'] == 'Time Played' and stat['value'] > 1:
                hero_details = (hero_name.title(), stats_list)

                return hero_details
