import random


class Card:
    def __init__(self, name, base_dmg, base_shield, base_mana, target="enemy", price=10):
        self.name = name
        self.damage = random.randint(*base_dmg) if isinstance(base_dmg, tuple) else base_dmg
        self.shield = random.randint(*base_shield) if isinstance(base_shield, tuple) else base_shield
        self.mana_cost = random.randint(*base_mana) if isinstance(base_mana, tuple) else base_mana
        self.target = target  # "enemy" или "self"
        self.price = price

    def apply_modifier(self):
        num_mods = random.randint(1, 3)
        for _ in range(num_mods):
            if random.randint(0, 1) == 0:
                continue
            mod_value = random.randint(-5, 5)
            mod_type = random.choice(['mana', 'shield', 'damage'])
            if mod_type == 'mana':
                self.mana_cost += mod_value
                self.name += f" (Ман:{'+' if mod_value >= 0 else ''}{mod_value})"
            elif mod_type == 'shield':
                self.shield += mod_value
                self.name += f" (Щит:{'+' if mod_value >= 0 else ''}{mod_value})"
            elif mod_type == 'damage':
                self.damage += mod_value
                self.name += f" (Ур:{'+' if mod_value >= 0 else ''}{mod_value})"

    def __str__(self):
        mana_text = f"Дает {-self.mana_cost} М" if self.mana_cost < 0 else f"Кост: {self.mana_cost} М"
        if self.target == "self":
            dmg_text = f"Хил: {-self.damage}" if self.damage < 0 else f"Сам-Урон: {self.damage}"
        else:
            dmg_text = f"Хил-Враг: {-self.damage}" if self.damage < 0 else f"Урон: {self.damage}"
        return f"[{self.name}] | {mana_text} | {dmg_text} | Щит: {self.shield} | Цель: {'Я' if self.target == 'self' else 'Враг'}"


def create_base_card(card_type):
    cfg = {
        "Удар":            ((2, 4),  (0, 0),  (0, 0),   "enemy", 5),
        "Медитация":       ((0, 0),  (0, 0),  (-6, -2), "self",  8),
        "Уклонение":       ((0, 0),  (0, 3),  (0, 0),   "self",  5),
        "Регенерация":     ((-2, 0), (0, 0),  (0, 0),   "self",  6),
        "Заклинание":      ((4, 8),  (0, 0),  (1, 3),   "enemy", 12),
        "Защитная Стойка": ((0, 0),  (4, 6),  (1, 3),   "self",  12),
        "Бинт":            ((-5, -3),(0, 0),  (1, 2),   "self",  10),
    }
    dmg, shd, mna, tgt, price = cfg[card_type]
    return Card(card_type, dmg, shd, mna, tgt, price)


class Creature:
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp
        self.shield = 0

    def take_damage(self, amount):
        actual_damage = max(0, amount - self.shield)
        self.hp -= actual_damage
        print(f"[Урон] {self.name} получает {actual_damage} урона (Входящий {amount} - Щит {self.shield}). ХП: {self.hp}")

    def heal(self, amount):
        self.hp += amount
        print(f"[Лечение] {self.name} восстанавливает {amount} ХП. ХП: {self.hp}")

    def add_shield(self, amount):
        self.shield += amount
        if amount >= 0:
            print(f"[Щит] {self.name} получает +{amount} щита. Щит: {self.shield}")
        else:
            self.shield = max(0, self.shield)
            print(f"[Уязвимость] {self.name} теряет {-amount} щита. Щит: {self.shield}")


class Enemy(Creature):
    def __init__(self, tier):
        super().__init__(f"Моб Тир-{tier}", hp=10 + tier * 5)
        self.tier = tier

    def process_turn_effects(self):
        print(f"\n[Эффекты] Модификаторы {self.name} (Количество: {self.tier}):")
        for _ in range(self.tier):
            mod_value = random.randint(-5, 5)
            mod_type = random.choice(['shield', 'regen', 'empty'])
            if mod_type == 'shield':
                self.shield = max(0, self.shield + mod_value)
                print(f"  -> Изменение Щита на {mod_value} (Текущий: {self.shield})")
            elif mod_type == 'regen':
                self.hp += mod_value
                print(f"  -> Регенерация изменила ХП на {mod_value} (Текущее: {self.hp})")
            else:
                print("  -> Пустой эффект")

    def attack_player(self, player):
        base_attack = random.randint(0, 12)
        print(f"[Атака] {self.name} наносит {base_attack} урона.")
        player.take_damage(base_attack)

    def end_turn(self):
        self.shield = 0


class Player(Creature):
    def __init__(self, name, hp, start_mana):
        super().__init__(name, hp)
        self.mana = start_mana
        self.gold = 0
        self.extra_decks = 2
        self.lives = 0
        self.kills = {t: 0 for t in range(1, 7)}
        self.deck = []
        self.hand = []
        self.special_cards = []
        self.deck_index = 0

    def create_deck(self):
        types = ["Удар", "Медитация", "Уклонение", "Регенерация", "Заклинание", "Защитная Стойка", "Бинт"]
        self.deck = []
        for t in types:
            for _ in range(6):
                self.deck.append(create_base_card(t))
        self.shuffle_deck()

    def shuffle_deck(self):
        if self.deck_index > 0:
            self.extra_decks -= 1
            print(f"\n[Внимание] Вы использовали запасную колоду! Осталось: {self.extra_decks}")
            if self.extra_decks < 0:
                print("[Поражение] У вас закончились запасные колоды!")
                exit()
        random.shuffle(self.deck)
        self.deck_index = 0
        print("[Колода] Основная колода перемешана!")

    def draw_hand(self):
        self.hand = []
        for _ in range(6):
            if self.deck_index >= len(self.deck):
                self.shuffle_deck()
            card = self.deck[self.deck_index]
            card_copy = Card(card.name, card.damage, card.shield, card.mana_cost, card.target)
            card_copy.apply_modifier()
            self.hand.append(card_copy)
            self.deck_index += 1
        for spec_card in self.special_cards:
            card_copy = Card(spec_card.name, spec_card.damage, spec_card.shield, spec_card.mana_cost, spec_card.target)
            card_copy.apply_modifier()
            self.hand.append(card_copy)
            print(f"[Инвентарь] Добавлена особая карта: {card_copy.name}")

    def end_turn(self):
        self.hand = []
        self.shield = 0


class GameMaster:
    def __init__(self, player):
        self.player = player
        self.room_names = {
            1: "Лагерь",
            2: "Торговец",
            3: "Алхимик",
            4: "Могила",
            5: "Наблюдательный пункт",
            6: "Гильдия охотников"
        }

    def generate_rooms(self, count=3):
        choices = []
        for _ in range(count):
            r_num = random.randint(1, 6)
            enemy_tier = random.randint(0, 6)
            choices.append((r_num, enemy_tier))
        return choices

    def play_card(self, card, enemy):
        p = self.player
        if card.target == "self":
            if card.damage < 0:
                p.heal(abs(card.damage))
            elif card.damage > 0:
                p.take_damage(card.damage)
            if card.shield != 0:
                p.add_shield(card.shield)
        else:
            if card.damage > 0:
                enemy.take_damage(card.damage)
            elif card.damage < 0:
                enemy.heal(abs(card.damage))
            if card.shield != 0:
                enemy.add_shield(card.shield)

    def start_room_loop(self):
        while self.player.hp > 0:
            print(f"\n============================================")
            print(f"Золото: {self.player.gold} | Колоды: {self.player.extra_decks} | Жизни: {self.player.lives}")
            print(f"ХП: {self.player.hp} | Макс. Мана: {self.player.mana}")
            print(f"============================================")

            room_options = self.generate_rooms(count=3)
            print("\n[Карта] Перед вами развилка путей:")
            for i, (r_num, tier) in enumerate(room_options):
                enemy_text = f"Враг Тир-{tier}" if tier > 0 else "Безопасная дорога"
                print(f"  {i + 1}. Комната: [{self.room_names[r_num]}] (В пути: {enemy_text})")

            try:
                choice = int(input("\nКуда направитесь? Введите номер: ")) - 1
                if not (0 <= choice < len(room_options)):
                    raise ValueError
            except ValueError:
                print("Неверный выбор.")
                continue

            chosen_room, chosen_tier = room_options[choice]

            if chosen_tier > 0:
                print(f"\n[Бой] На вас нападает враг Тир-{chosen_tier}!")
                enemy = Enemy(chosen_tier)
                self.battle(enemy)

                if self.player.hp <= 0:
                    if self.player.lives > 0:
                        self.player.lives -= 1
                        self.player.hp = 15
                        self.player.mana = 5
                        print("\n[Воскрешение] Вы воскресли благодаря магии Могилы! ХП: 15, Мана: 5. Но вы не знаете где вы.")
                        continue
                    else:
                        print("\n[Поражение] Игра окончена. Вы погибли окончательно.")
                        break
                else:
                    self.player.kills[chosen_tier] += 1
                    print(f"[Победа] Убийство Тир-{chosen_tier} записано в гильдию.")

            self.enter_room(chosen_room)

    def battle(self, enemy):
        while self.player.hp > 0 and enemy.hp > 0:
            print(f"\n--- Ваш ход (Индекс колоды: {self.player.deck_index}/{len(self.player.deck)}) ---")
            self.player.draw_hand()

            while True:
                print(f"\nВы: ХП {self.player.hp} | Мана {self.player.mana} | Щит {self.player.shield}")
                print(f"Враг: ХП {enemy.hp} | Щит {enemy.shield}")
                for i, card in enumerate(self.player.hand):
                    print(f"  {i + 1}. {card}")
                print("  0. Закончить ход")

                try:
                    act = int(input("Выберите карту: "))
                except ValueError:
                    continue

                if act == 0:
                    break

                if 1 <= act <= len(self.player.hand):
                    card = self.player.hand[act - 1]
                    if card.mana_cost > 0 and self.player.mana < card.mana_cost:
                        print("[Ошибка] Маны недостаточно!")
                        continue
                    card = self.player.hand.pop(act - 1)
                    self.player.mana -= card.mana_cost
                    self.play_card(card, enemy)

            if enemy.hp > 0:
                enemy.process_turn_effects()
                enemy.attack_player(self.player)
                enemy.end_turn()

            self.player.end_turn()

    def enter_room(self, room_type):
        print(f"\n[Комната] Вы зашли в: [{self.room_names[room_type]}]")

        if room_type == 1:  # Лагерь
            self.player.hp += 5
            self.player.mana += 2
            self.player.mana = self.player.mana
            print(f"Восстановлено 5 ХП. Макс. Мана увеличилась на 2 (теперь {self.player.mana}).")
            print("\nВ лагере вы можете:")
            print("  1. Заменить карту из Колоды на карту из Инвентаря")
            print("  2. Заменить карту из Инвентаря на карту из Колоды")
            print("  0. Уйти")
            while True:
                ch = input("Выбор: ").strip()
                if ch == "0":
                    break
                elif ch == "1":
                    if not self.player.special_cards:
                        print("Инвентарь пуст.")
                        continue
                    if not self.player.deck:
                        print("Колода пуста.")
                        continue
                    print("Карты в Инвентаре:")
                    for i, c in enumerate(self.player.special_cards):
                        print(f"  {i + 1}. {c}")
                    try:
                        si = int(input("Выберите карту из инвентаря: ")) - 1
                        if not (0 <= si < len(self.player.special_cards)):
                            raise ValueError
                    except ValueError:
                        print("Неверный выбор.")
                        continue
                    print("Карты в Колоде:")
                    for i, c in enumerate(self.player.deck):
                        print(f"  {i + 1}. {c}")
                    try:
                        di = int(input("Выберите карту из колоды для замены: ")) - 1
                        if not (0 <= di < len(self.player.deck)):
                            raise ValueError
                    except ValueError:
                        print("Неверный выбор.")
                        continue
                    spec = self.player.special_cards.pop(si)
                    deck_card = self.player.deck.pop(di)
                    self.player.deck.insert(di, spec)
                    self.player.special_cards.insert(si, deck_card)
                    print(f"Обменяли [{spec.name}] из инвентаря на [{deck_card.name}] из колоды.")
                elif ch == "2":
                    if not self.player.deck:
                        print("Колода пуста.")
                        continue
                    print("Карты в Колоде:")
                    for i, c in enumerate(self.player.deck):
                        print(f"  {i + 1}. {c}")
                    try:
                        di = int(input("Выберите карту из колоды: ")) - 1
                        if not (0 <= di < len(self.player.deck)):
                            raise ValueError
                    except ValueError:
                        print("Неверный выбор.")
                        continue
                    if not self.player.special_cards:
                        print("Инвентарь пуст.")
                        continue
                    print("Карты в Инвентаре:")
                    for i, c in enumerate(self.player.special_cards):
                        print(f"  {i + 1}. {c}")
                    try:
                        si = int(input("Выберите карту из инвентаря для замены: ")) - 1
                        if not (0 <= si < len(self.player.special_cards)):
                            raise ValueError
                    except ValueError:
                        print("Неверный выбор.")
                        continue
                    deck_card = self.player.deck.pop(di)
                    spec = self.player.special_cards.pop(si)
                    self.player.deck.insert(di, spec)
                    self.player.special_cards.insert(si, deck_card)
                    print(f"Обменяли [{deck_card.name}] из колоды на [{spec.name}] из инвентаря.")
                else:
                    print("Неверный выбор.")

        elif room_type == 2:  # Торговец
            print("Приветствую тебя, охотник! Посмотри, что можешь купить.")
            while True:
                print("0. Выйти из магазина."
                      "1. Купить Запасную Колоду (15 золота)"
                      "2. Купить набор из трёх карт.")
                ch = input("Выбор: ").strip()
                if ch == "0":
                    break
                elif ch == "1" and self.player.gold >= 15:
                    self.player.gold -= 15
                    self.player.extra_decks += 1
                    print("Куплена колода!")
                elif ch == "2":
                    all_types = ["Удар", "Медитация", "Уклонение", "Регенерация", "Заклинание", "Защитная Стойка", "Бинт"]
                    sets = []
                    for _ in range(3):
                        bundle = []
                        chosen_types = random.sample(all_types, 3)
                        for t in chosen_types:
                            c = create_base_card(t)
                            bundle.append(c)
                        bundle_price = sum(c.price for c in bundle)
                        sets.append((bundle, bundle_price))

                    for i, (bundle, price) in enumerate(sets):
                        print(f"\n  Набор {i + 1} ({price} золота):")
                        for c in bundle:
                            print(f"    - {c}")

                    print("\n  0. Уйти")
                    try:
                        ch = int(input("Выберите набор (1-3): ")) - 1
                        if 0 <= ch < 3:
                            bundle, price = sets[ch]
                            if self.player.gold >= price:
                                self.player.gold -= price
                                for c in bundle:
                                    self.player.deck.append(c)
                                print(f"Куплен набор из {len(bundle)} карт!")
                            else:
                                print(f"Не хватает золота! Нужно {price}, у вас {self.player.gold}.")
                    except ValueError:
                        pass

        elif room_type == 3:  # Ловца Душ
            print("Лаборатория Ловца Душ. Особые карты всегда добавляются в руку в начале каждого хода.")
            types = ["Удар", "Медитация", "Уклонение"]
            showcase = []
            for t in types:
                c = create_base_card(t)
                c.price = max(1, 20 + random.randint(-12, 12))
                showcase.append(c)

            for i, c in enumerate(showcase):
                print(f"  {i + 1}. Особый {c.name} | Цена: {c.price} золота")
            print("  0. Выйти")
            try:
                ch = int(input("Что выберете? "))
                if 1 <= ch <= 3:
                    chosen_spec = showcase[ch - 1]
                    if self.player.gold >= chosen_spec.price:
                        self.player.gold -= chosen_spec.price
                        self.player.special_cards.append(chosen_spec)
                        print(f"Особая карта [{chosen_spec.name}] куплена и помещена в инвентарь!")
                    else:
                        print("Не хватает золота!")
            except ValueError:
                pass

        elif room_type == 4:  # Могила
            self.player.lives += 1
            print("Вы коснулись древней Могилы. Запас жизней увеличен на +1!")

        elif room_type == 5:  # Наблюдательный пункт
            print("Отсюда видно абсолютно всё! Вы получаете расширенный выбор из 6 комнат.")
            options = self.generate_rooms(count=6)
            print("\n[Карта] Эксклюзивные направления с вышки:")
            for i, (r_num, tier) in enumerate(options):
                enemy_text = f"Враг Тир-{tier}" if tier > 0 else "Безопасная дорога"
                print(f"  {i + 1}. Комната: [{self.room_names[r_num]}] (В пути: {enemy_text})")
            try:
                choice = int(input("\nКуда направитесь? Введите номер: ")) - 1
                if 0 <= choice < 6:
                    r_num, tier = options[choice]
                    if tier > 0:
                        print(f"[Бой] Засада на тайной тропе! Враг Тир-{tier}")
                        self.battle(Enemy(tier))
                    if self.player.hp > 0:
                        self.enter_room(r_num)
            except ValueError:
                print("Вы замешкались и спустились вниз.")

        elif room_type == 6:  # Гильдия охотников
            total_payout = 0
            print("\n[Гильдия] Ваши записи об убийствах:")
            for tier, count in self.player.kills.items():
                if count > 0:
                    reward = tier * 10 * count
                    total_payout += reward
                    print(f"  Тир-{tier}: {count} убийств -> {reward} монет")
                    self.player.kills[tier] = 0
            self.player.gold += total_payout
            print(f"Итого выплачено: {total_payout} монет.")


if __name__ == "__main__":
    print("Добро пожаловать в карточное подземелье!")
    name = input("Введите имя персонажа: ")
    player = Player(name=name, hp=30, start_mana=10)
    player.create_deck()
    gm = GameMaster(player)
    gm.start_room_loop()