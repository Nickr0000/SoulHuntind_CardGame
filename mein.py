import random
import json
import os

DECKS_FILE = "decks.json"

ALL_CARD_TYPES = ["Strike", "Meditation", "Dodge", "Regeneration", "Spell", "Guard Stance", "Bandage"]

CARD_CFG = {
    "Strike":       ((2, 4),  (0, 0), (0, 0),   "enemy", 5),
    "Meditation":   ((0, 0),  (0, 0), (-6, -2), "self",  8),
    "Dodge":        ((0, 0),  (0, 3), (0, 0),   "self",  5),
    "Regeneration": ((-2, 0), (0, 0), (0, 0),   "self",  6),
    "Spell":        ((4, 8),  (0, 0), (1, 3),   "enemy", 12),
    "Guard Stance": ((0, 0),  (4, 6), (1, 3),   "self",  12),
    "Bandage":      ((-5, -3),(0, 0), (1, 2),   "self",  10),
}


# ==================================================================================== CARDS


class Card:
    def __init__(self, name, base_dmg, base_shield, base_mana, target="enemy", price=10):
        self.name = name
        self.damage = random.randint(*base_dmg) if isinstance(base_dmg, tuple) else base_dmg
        self.shield = random.randint(*base_shield) if isinstance(base_shield, tuple) else base_shield
        self.mana_cost = random.randint(*base_mana) if isinstance(base_mana, tuple) else base_mana
        self.target = target
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
                self.name += f" (Man:{'+' if mod_value >= 0 else ''}{mod_value})"
            elif mod_type == 'shield':
                self.shield += mod_value
                self.name += f" (Shld:{'+' if mod_value >= 0 else ''}{mod_value})"
            elif mod_type == 'damage':
                self.damage += mod_value
                self.name += f" (Dmg:{'+' if mod_value >= 0 else ''}{mod_value})"

    def __str__(self):
        mana_text = f"Gives {-self.mana_cost} M" if self.mana_cost < 0 else f"Cost: {self.mana_cost} M"
        if self.target == "self":
            dmg_text = f"Heal: {-self.damage}" if self.damage < 0 else f"Self-Dmg: {self.damage}"
        else:
            dmg_text = f"Heal-Enemy: {-self.damage}" if self.damage < 0 else f"Dmg: {self.damage}"
        tgt = "Self" if self.target == "self" else "Enemy"
        return f"[{self.name}] | {mana_text} | {dmg_text} | Shield: {self.shield} | Target: {tgt}"


def create_base_card(card_type):
    dmg, shd, mna, tgt, price = CARD_CFG[card_type]
    return Card(card_type, dmg, shd, mna, tgt, price)


# ==================================================================================== DECK MANAGEMENT (JSON)


def load_decks():
    if not os.path.exists(DECKS_FILE):
        return {}
    with open(DECKS_FILE, "r") as f:
        content = f.read().strip()
        if not content:
            return {}
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            print("[Warning] decks.json is corrupted. Starting with empty deck list.")
            return {}


def save_decks(decks):
    with open(DECKS_FILE, "w") as f:
        json.dump(decks, f, indent=2)


def deck_to_json(deck):
    result = {}
    for card in deck:
        result[card.name] = result.get(card.name, 0) + 1
    return result


def deck_from_json(data):
    deck = []
    for card_type, count in data.items():
        if card_type not in CARD_CFG:
            continue
        for _ in range(count):
            deck.append(create_base_card(card_type))
    return deck


def default_deck():
    deck = []
    for t in ALL_CARD_TYPES:
        for _ in range(6):
            deck.append(create_base_card(t))
    return deck


def deck_builder_menu():
    counts = {t: 0 for t in ALL_CARD_TYPES}
    while True:
        print("\n--- Deck Builder ---")
        total = sum(counts.values())
        for i, t in enumerate(ALL_CARD_TYPES):
            print(f"  {i + 1}. {t}: {counts[t]} cards")
        print(f"  Total cards: {total}")
        print("  S. Save and use this deck")
        print("  0. Cancel (use default deck)")
        ch = input("Add card by number, or S/0: ").strip().lower()
        if ch == "0":
            return None
        if ch == "s":
            if total == 0:
                print("Deck is empty. Add some cards first.")
                continue
            return [create_base_card(t) for t, c in counts.items() for _ in range(c)]
        try:
            idx = int(ch) - 1
            if 0 <= idx < len(ALL_CARD_TYPES):
                counts[ALL_CARD_TYPES[idx]] += 1
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")


def main_menu():
    while True:
        print("\n===============================================")
        print("   CARD DUNGEON - MAIN MENU")
        print("===============================================")
        print("  1. Start with default deck")
        print("  2. Build a new deck")
        print("  3. Load a saved deck")
        print("  4. Delete a saved deck")
        print("  0. Quit")
        ch = input("Choice: ").strip()

        if ch == "0":
            print("Goodbye.")
            exit()

        elif ch == "1":
            return default_deck()

        elif ch == "2":
            deck = deck_builder_menu()
            if deck is None:
                continue
            decks = load_decks()
            name = input("Save deck as (leave blank to not save): ").strip()
            if name:
                decks[name] = deck_to_json(deck)
                save_decks(decks)
                print(f"Deck '{name}' saved.")
            return deck

        elif ch == "3":
            decks = load_decks()
            if not decks:
                print("No saved decks found.")
                continue
            print("\nSaved decks:")
            names = list(decks.keys())
            for i, n in enumerate(names):
                total = sum(decks[n].values())
                print(f"  {i + 1}. {n} ({total} cards)")
            try:
                idx = int(input("Choose deck number: ")) - 1
                if not (0 <= idx < len(names)):
                    raise ValueError
            except ValueError:
                print("Invalid choice.")
                continue
            return deck_from_json(decks[names[idx]])

        elif ch == "4":
            decks = load_decks()
            if not decks:
                print("No saved decks found.")
                continue
            names = list(decks.keys())
            for i, n in enumerate(names):
                print(f"  {i + 1}. {n}")
            try:
                idx = int(input("Delete deck number: ")) - 1
                if not (0 <= idx < len(names)):
                    raise ValueError
            except ValueError:
                print("Invalid choice.")
                continue
            del decks[names[idx]]
            save_decks(decks)
            print(f"Deck '{names[idx]}' deleted.")

        else:
            print("Invalid choice.")


# ==================================================================================== CREATURES


class Creature:
    def __init__(self, name, hp):
        self.name = name
        self.hp = hp
        self.shield = 0

    def take_damage(self, amount):
        actual_damage = max(0, amount - self.shield)
        self.hp -= actual_damage
        print(f"[Damage] {self.name} takes {actual_damage} dmg (Incoming {amount} - Shield {self.shield}). HP: {self.hp}")

    def heal(self, amount):
        self.hp += amount
        print(f"[Heal] {self.name} restores {amount} HP. HP: {self.hp}")

    def add_shield(self, amount):
        self.shield += amount
        if amount >= 0:
            print(f"[Shield] {self.name} gains +{amount} shield. Shield: {self.shield}")
        else:
            self.shield = max(0, self.shield)
            print(f"[Vulnerable] {self.name} loses {-amount} shield. Shield: {self.shield}")


class Enemy(Creature):
    def __init__(self, tier):
        super().__init__(f"Mob Tier-{tier}", hp=10 + tier * 5)
        self.tier = tier

    def process_turn_effects(self):
        print(f"\n[Effects] {self.name} rolls modifiers (Count: {self.tier}):")
        for _ in range(self.tier):
            mod_value = random.randint(-5, 5)
            mod_type = random.choice(['shield', 'regen', 'empty'])
            if mod_type == 'shield':
                self.shield = max(0, self.shield + mod_value)
                print(f"  -> Shield changed by {mod_value} (Now: {self.shield})")
            elif mod_type == 'regen':
                self.hp += mod_value
                print(f"  -> Regen changed HP by {mod_value} (Now: {self.hp})")
            else:
                print("  -> Empty effect")

    def attack_player(self, player):
        base_attack = random.randint(0, 12)
        print(f"[Attack] {self.name} deals {base_attack} damage.")
        player.take_damage(base_attack)

    def drop_card(self):
        roll = random.randint(1, 5)
        if roll <= 2:
            card_type = random.choice(ALL_CARD_TYPES)
            card = create_base_card(card_type)
            print(f"[Drop] The enemy dropped a card: {card.name}!")
            return card
        return None

    def end_turn(self):
        self.shield = 0


# ==================================================================================== PLAYER


class Player(Creature):
    def __init__(self, name, hp, start_mana, deck):
        super().__init__(name, hp)
        self.mana = start_mana
        self.max_mana = start_mana
        self.gold = 0
        self.extra_decks = 2
        self.lives = 0
        self.kills = {t: 0 for t in range(1, 7)}
        self.deck = deck
        self.hand = []
        self.special_cards = []
        self.deck_index = 0
        random.shuffle(self.deck)

    def shuffle_deck(self):
        if self.deck_index > 0:
            self.extra_decks -= 1
            print(f"\n[Warning] You used a spare deck! Remaining: {self.extra_decks}")
            if self.extra_decks < 0:
                print("[Defeat] You ran out of spare decks!")
                exit()
        random.shuffle(self.deck)
        self.deck_index = 0
        print("[Deck] Main deck reshuffled!")

    def draw_hand(self):
        self.hand = []
        for _ in range(6):
            if self.deck_index >= len(self.deck):
                self.shuffle_deck()
            card = self.deck[self.deck_index]
            card_copy = Card(card.name, card.damage, card.shield, card.mana_cost, card.target, card.price)
            card_copy.apply_modifier()
            self.hand.append(card_copy)
            self.deck_index += 1
        for spec_card in self.special_cards:
            card_copy = Card(spec_card.name, spec_card.damage, spec_card.shield, spec_card.mana_cost, spec_card.target, spec_card.price)
            card_copy.apply_modifier()
            self.hand.append(card_copy)
            print(f"[Inventory] Special card added to hand: {card_copy.name}")

    def add_card_to_deck(self, card):
        self.deck.append(card)
        print(f"[Deck] {card.name} added to your deck.")

    def end_turn(self):
        self.hand = []
        self.shield = 0
        self.mana = self.max_mana


# ==================================================================================== GAME MASTER


class GameMaster:
    def __init__(self, player):
        self.player = player
        self.room_names = {
            1: "Camp",
            2: "Merchant",
            3: "Soul Catcher",  # Алхимик
            4: "Grave",
            5: "Watchtower",
            6: "Hunter's Guild"
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
            print(f"Gold: {self.player.gold} | Decks: {self.player.extra_decks} | Lives: {self.player.lives}")
            print(f"HP: {self.player.hp} | Max Mana: {self.player.max_mana}")
            print(f"============================================")

            room_options = self.generate_rooms(count=3)
            print("\n[Map] A fork in the road:")
            for i, (r_num, tier) in enumerate(room_options):
                enemy_text = f"Enemy Tier-{tier}" if tier > 0 else "Safe road"
                print(f"  {i + 1}. Room: [{self.room_names[r_num]}] (On the way: {enemy_text})")

            try:
                choice = int(input("\nWhere will you go? Enter number: ")) - 1
                if not (0 <= choice < len(room_options)):
                    raise ValueError
            except ValueError:
                print("Invalid choice.")
                continue

            chosen_room, chosen_tier = room_options[choice]

            if chosen_tier > 0:
                print(f"\n[Combat] An enemy attacks! Tier-{chosen_tier}!")
                enemy = Enemy(chosen_tier)
                self.battle(enemy)

                if self.player.hp <= 0:
                    if self.player.lives > 0:
                        self.player.lives -= 1
                        self.player.hp = 15
                        self.player.mana = 5
                        self.player.max_mana = 5
                        print("\n[Resurrection] You were revived by the magic of the Grave! HP: 15, Mana: 5. But you don't know where you are.")
                        continue
                    else:
                        print("\n[Defeat] Game over. You have died for good.")
                        break
                else:
                    self.player.kills[chosen_tier] += 1
                    print(f"[Victory] Tier-{chosen_tier} kill recorded with the guild.")
                    dropped = enemy.drop_card()
                    if dropped:
                        add = input("Add dropped card to your deck? (1 - Yes, 0 - No): ").strip()
                        if add == "1":
                            self.player.add_card_to_deck(dropped)

            self.enter_room(chosen_room)

    def battle(self, enemy):
        while self.player.hp > 0 and enemy.hp > 0:
            print(f"\n--- Your Turn (Deck index: {self.player.deck_index}/{len(self.player.deck)}) ---")
            self.player.draw_hand()

            while True:
                print(f"\nYou: HP {self.player.hp} | Mana {self.player.mana} | Shield {self.player.shield}")
                print(f"Enemy: HP {enemy.hp} | Shield {enemy.shield}")
                for i, card in enumerate(self.player.hand):
                    print(f"  {i + 1}. {card}")
                print("  0. End turn")

                try:
                    act = int(input("Choose card: "))
                except ValueError:
                    continue

                if act == 0:
                    break

                if 1 <= act <= len(self.player.hand):
                    card = self.player.hand[act - 1]
                    if card.mana_cost > 0 and self.player.mana < card.mana_cost:
                        print("[Error] Not enough mana!")
                        continue
                    card = self.player.hand.pop(act - 1)
                    self.player.mana -= card.mana_cost
                    self.play_card(card, enemy)

            if enemy.hp > 0:
                enemy.process_turn_effects()
                enemy.attack_player(self.player)

            self.player.end_turn()
            if enemy.hp > 0:
                enemy.end_turn()

    def enter_room(self, room_type):
        print(f"\n[Room] You entered: [{self.room_names[room_type]}]")

        if room_type == 1:  # Camp
            self.player.hp += 5
            self.player.max_mana += 2
            self.player.mana = self.player.max_mana
            print(f"Restored 5 HP. Max Mana increased by 2 (now {self.player.max_mana}).")
            print("\nAt camp you can:")
            print("  1. Swap a Deck card for an Inventory card")
            print("  2. Swap an Inventory card for a Deck card")
            print("  0. Leave")
            while True:
                ch = input("Choice: ").strip()
                if ch == "0":
                    break
                elif ch in ("1", "2"):
                    if not self.player.special_cards:
                        print("Inventory is empty.")
                        continue
                    if not self.player.deck:
                        print("Deck is empty.")
                        continue

                    if ch == "1":
                        print("Inventory cards:")
                        for i, c in enumerate(self.player.special_cards):
                            print(f"  {i + 1}. {c}")
                        try:
                            si = int(input("Choose inventory card: ")) - 1
                            if not (0 <= si < len(self.player.special_cards)):
                                raise ValueError
                        except ValueError:
                            print("Invalid choice.")
                            continue
                        print("Deck cards:")
                        for i, c in enumerate(self.player.deck):
                            print(f"  {i + 1}. {c}")
                        try:
                            di = int(input("Choose deck card to replace: ")) - 1
                            if not (0 <= di < len(self.player.deck)):
                                raise ValueError
                        except ValueError:
                            print("Invalid choice.")
                            continue
                        spec = self.player.special_cards.pop(si)
                        deck_card = self.player.deck.pop(di)
                        self.player.deck.insert(di, spec)
                        self.player.special_cards.insert(si, deck_card)
                        print(f"Swapped [{spec.name}] from inventory with [{deck_card.name}] from deck.")
                    else:
                        print("Deck cards:")
                        for i, c in enumerate(self.player.deck):
                            print(f"  {i + 1}. {c}")
                        try:
                            di = int(input("Choose deck card: ")) - 1
                            if not (0 <= di < len(self.player.deck)):
                                raise ValueError
                        except ValueError:
                            print("Invalid choice.")
                            continue
                        print("Inventory cards:")
                        for i, c in enumerate(self.player.special_cards):
                            print(f"  {i + 1}. {c}")
                        try:
                            si = int(input("Choose inventory card to replace: ")) - 1
                            if not (0 <= si < len(self.player.special_cards)):
                                raise ValueError
                        except ValueError:
                            print("Invalid choice.")
                            continue
                        deck_card = self.player.deck.pop(di)
                        spec = self.player.special_cards.pop(si)
                        self.player.deck.insert(di, spec)
                        self.player.special_cards.insert(si, deck_card)
                        print(f"Swapped [{deck_card.name}] from deck with [{spec.name}] from inventory.")
                else:
                    print("Invalid choice.")

        elif room_type == 2:  # Merchant
            print("Greetings, hunter! See what you can buy.")
            while True:
                print("\n  1. Buy a Spare Deck (15 gold)")
                print("  2. Buy a set of three cards")
                print("  0. Leave")
                ch = input("Choice: ").strip()
                if ch == "0":
                    break
                elif ch == "1":
                    if self.player.gold >= 15:
                        self.player.gold -= 15
                        self.player.extra_decks += 1
                        print("Spare deck purchased!")
                    else:
                        print(f"Not enough gold! Need 15, you have {self.player.gold}.")
                elif ch == "2":
                    sets = []
                    for _ in range(3):
                        bundle = []
                        chosen_types = random.sample(ALL_CARD_TYPES, 3)
                        for t in chosen_types:
                            bundle.append(create_base_card(t))
                        bundle_price = sum(c.price for c in bundle)
                        sets.append((bundle, bundle_price))

                    for i, (bundle, price) in enumerate(sets):
                        print(f"\n  Set {i + 1} ({price} gold):")
                        for c in bundle:
                            print(f"    - {c}")
                    print("  0. Cancel")

                    try:
                        pick = int(input("Choose set (1-3): ")) - 1
                        if 0 <= pick < 3:
                            bundle, price = sets[pick]
                            if self.player.gold >= price:
                                self.player.gold -= price
                                for c in bundle:
                                    self.player.deck.append(c)
                                print(f"Bought a set of {len(bundle)} cards!")
                            else:
                                print(f"Not enough gold! Need {price}, you have {self.player.gold}.")
                    except ValueError:
                        pass
                else:
                    print("Invalid choice.")

        elif room_type == 3:  # Soul Catcher
            print("Soul Catcher's Lab. Special cards are always added to your hand at the start of each turn.")
            showcase = []
            for t in random.sample(ALL_CARD_TYPES, 3):
                c = create_base_card(t)
                c.price = max(1, 20 + random.randint(-12, 12))
                showcase.append(c)

            for i, c in enumerate(showcase):
                print(f"  {i + 1}. Special {c.name} | Price: {c.price} gold")
            print("  0. Leave")
            try:
                ch = int(input("Your choice? "))
                if 1 <= ch <= len(showcase):
                    chosen_spec = showcase[ch - 1]
                    if self.player.gold >= chosen_spec.price:
                        self.player.gold -= chosen_spec.price
                        self.player.special_cards.append(chosen_spec)
                        print(f"Special card [{chosen_spec.name}] bought and placed in inventory!")
                    else:
                        print("Not enough gold!")
            except ValueError:
                pass

        elif room_type == 4:  # Grave
            self.player.lives += 1
            print("You touched an ancient Grave. Extra lives increased by +1!")

        elif room_type == 5:  # Watchtower
            print("You can see everything from here! You get an expanded choice of 6 rooms.")
            options = self.generate_rooms(count=6)
            print("\n[Map] Exclusive directions from the tower:")
            for i, (r_num, tier) in enumerate(options):
                enemy_text = f"Enemy Tier-{tier}" if tier > 0 else "Safe road"
                print(f"  {i + 1}. Room: [{self.room_names[r_num]}] (On the way: {enemy_text})")
            try:
                choice = int(input("\nWhere will you go? Enter number: ")) - 1
                if 0 <= choice < 6:
                    r_num, tier = options[choice]
                    if tier > 0:
                        print(f"[Combat] Ambush on the secret path! Tier-{tier}")
                        self.battle(Enemy(tier))
                    if self.player.hp > 0:
                        self.enter_room(r_num)
            except ValueError:
                print("You hesitated and climbed back down.")

        elif room_type == 6:  # Hunter's Guild
            total_payout = 0
            print("\n[Guild] Your kill records:")
            any_kills = False
            for tier, count in self.player.kills.items():
                if count > 0:
                    any_kills = True
                    reward = tier * 10 * count
                    total_payout += reward
                    print(f"  Tier-{tier}: {count} kills -> {reward} coins")
                    self.player.kills[tier] = 0
            if not any_kills:
                print("  No kills recorded yet.")
            self.player.gold += total_payout
            print(f"Total paid out: {total_payout} coins.")


# # ==================================================================================== ENTRY POINT


if __name__ == "__main__":
    print("Welcome to the Card Dungeon!")
    deck = main_menu()
    name = input("Enter character name: ").strip() or "Hunter"
    player = Player(name=name, hp=30, start_mana=10, deck=deck)
    gm = GameMaster(player)
    gm.start_room_loop()