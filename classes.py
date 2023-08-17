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

    def format_details(self, hero_name, stats_dictionary):
        stats_dictionary_keys = stats_dictionary.keys()

        hero_stats = []
        for key in stats_dictionary_keys:
            stat_name = self.split_camel_case(key)
            if stat_name == 'Hero Damage Done':
                stat_name = 'Damage Done'

            stat_value = int(stats_dictionary[key])

            current_stat = {'name': stat_name, 'value': stat_value}

            hero_stats.append(current_stat)

        for stat in hero_stats:
            if stat['name'] == 'Time Played' and stat['value'] > 60:
                hero_details = (hero_name.title(), hero_stats)

                return hero_details
