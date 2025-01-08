import random
from dataclasses import dataclass
from enum import Enum
from typing import List

# Game configuration
HAND_SIZE = 8          # Number of cards in hand
PLAYS_PER_ROUND = 3    # Number of hands you can play per round
DISCARDS_PER_ROUND = 4 # Number of discard actions per round
MAX_DISCARDS = 3       # Maximum cards you can discard in one action

class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class Rank(Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

@dataclass
class Card:
    rank: Rank
    suit: Suit
    
    def __str__(self):
        return f"{self.rank.value}{self.suit.value}"
    
    def value(self) -> int:
        values = {
            Rank.TWO: 2,
            Rank.THREE: 3,
            Rank.FOUR: 4,
            Rank.FIVE: 5,
            Rank.SIX: 6,
            Rank.SEVEN: 7,
            Rank.EIGHT: 8,
            Rank.NINE: 9,
            Rank.TEN: 10,
            Rank.JACK: 11,
            Rank.QUEEN: 12,
            Rank.KING: 13,
            Rank.ACE: 14
        }
        return values[self.rank]

class HandType(Enum):
    HIGH_CARD = "High Card"
    PAIR = "Pair"
    TWO_PAIR = "Two Pair"
    THREE_OF_KIND = "Three of a Kind"
    STRAIGHT = "Straight"
    FLUSH = "Flush"
    FULL_HOUSE = "Full House"
    FOUR_OF_KIND = "Four of a Kind"
    STRAIGHT_FLUSH = "Straight Flush"
    ROYAL_FLUSH = "Royal Flush"

class Game:
    def __init__(self):
        self.deck = self._create_deck()
        self.hand: List[Card] = []
        self.score = 0
        self.round_score = 0
        self.chips = 1000
        self.plays_remaining = PLAYS_PER_ROUND
        self.discards_remaining = DISCARDS_PER_ROUND
        self.sort_by_rank = True  # Default sorting by rank
        self.hand_counts = {hand_type: 0 for hand_type in HandType}
        self.base_multipliers = {
            HandType.ROYAL_FLUSH: 5.0,
            HandType.STRAIGHT_FLUSH: 4.0,
            HandType.FOUR_OF_KIND: 3.0,
            HandType.FULL_HOUSE: 2.5,
            HandType.FLUSH: 2.0,
            HandType.STRAIGHT: 2.0,
            HandType.THREE_OF_KIND: 1.5,
            HandType.TWO_PAIR: 1.3,
            HandType.PAIR: 1.2,
            HandType.HIGH_CARD: 1.0
        }
        random.shuffle(self.deck)
        self.draw_hand()
    
    def _create_deck(self) -> List[Card]:
        return [Card(rank, suit) 
                for suit in Suit 
                for rank in Rank]

    def sort_hand(self):
        """Sort the hand based on current sorting preference"""
        def suit_order(suit: Suit) -> int:
            order = {
                Suit.CLUBS: 0,    # ♣
                Suit.DIAMONDS: 1, # ♦
                Suit.HEARTS: 2,   # ♥
                Suit.SPADES: 3    # ♠
            }
            return order[suit]

        if self.sort_by_rank:
            # Sort by rank value first, then by suit order
            self.hand.sort(key=lambda card: (card.value(), suit_order(card.suit)))
        else:
            # Sort by suit order first, then by rank value
            self.hand.sort(key=lambda card: (suit_order(card.suit), card.value()))

    def draw_hand(self):
        """Draw a new hand and sort it"""
        self.hand.clear()  # Clear existing hand
        for _ in range(HAND_SIZE):
            if self.deck:
                self.hand.append(self.deck.pop())
            else:  # Reshuffle if deck is empty
                self.deck = self._create_deck()
                random.shuffle(self.deck)
                self.hand.append(self.deck.pop())
        self.sort_hand()  # Sort the new hand

    def discard_cards(self, indices: List[int]) -> bool:
        """Discard specific cards and draw replacements. Returns False if not enough discards remaining."""
        if len(indices) > MAX_DISCARDS:
            return False
        
        # Sort indices in reverse order to avoid shifting problems
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(self.hand):
                self.hand.pop(index)
        
        # Draw new cards to replace discarded ones
        while len(self.hand) < HAND_SIZE:
            if self.deck:
                self.hand.append(self.deck.pop())
            else:
                self.deck = self._create_deck()
                random.shuffle(self.deck)
                self.hand.append(self.deck.pop())
        
        self.sort_hand()  # Sort after drawing new cards
        self.discards_remaining -= 1
        return True

    def get_hand_multiplier(self, hand_type: HandType) -> float:
        """Calculate multiplier for a hand type based on how many times it's been played"""
        base = self.base_multipliers[hand_type]
        plays = self.hand_counts[hand_type]
        # Increase multiplier by 10% for each time this hand type has been played
        return base * (1 + (plays * 0.1))

    def evaluate_hand(self, selected_cards: List[Card] = None) -> tuple[HandType, int]:
        """Evaluate a poker hand. Returns (hand_type, base_points)"""
        if selected_cards is None:
            selected_cards = self.hand
        
        if len(selected_cards) < 1 or len(selected_cards) > 5:
            raise ValueError("Must play 1-5 cards")
            
        if len(selected_cards) < 5:
            # For hands smaller than 5, score based on highest card plus small bonus for each card
            high_card = max(card.value() for card in selected_cards)
            return HandType.HIGH_CARD, high_card + len(selected_cards)
            
        # Sort hand by value
        sorted_hand = sorted(selected_cards, key=lambda x: x.value())
        values = [card.value() for card in sorted_hand]
        suits = [card.suit for card in sorted_hand]
        
        # Check for flush
        is_flush = len(set(suits)) == 1
        
        # Check for straight
        is_straight = (max(values) - min(values) == 4 and len(set(values)) == 5)
        
        # Count occurrences of each value
        value_counts = {}
        for value in values:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        # Royal Flush
        if is_flush and values == [10, 11, 12, 13, 14]:
            return HandType.ROYAL_FLUSH, 100
        
        # Straight Flush
        if is_flush and is_straight:
            return HandType.STRAIGHT_FLUSH, 75
        
        # Four of a Kind
        if 4 in value_counts.values():
            return HandType.FOUR_OF_KIND, 50
        
        # Full House
        if set(value_counts.values()) == {2, 3}:
            return HandType.FULL_HOUSE, 25
        
        # Flush
        if is_flush:
            return HandType.FLUSH, 20
        
        # Straight
        if is_straight:
            return HandType.STRAIGHT, 15
        
        # Three of a Kind
        if 3 in value_counts.values():
            return HandType.THREE_OF_KIND, 10
        
        # Two Pair
        if list(value_counts.values()).count(2) == 2:
            return HandType.TWO_PAIR, 5
        
        # Pair
        if 2 in value_counts.values():
            return HandType.PAIR, 2
        
        # High Card
        return HandType.HIGH_CARD, 1

    def start_new_round(self):
        """Reset round-specific variables and start a new round."""
        self.round_score = 0
        self.plays_remaining = PLAYS_PER_ROUND
        self.discards_remaining = DISCARDS_PER_ROUND
        self.deck = self._create_deck()
        random.shuffle(self.deck)
        self.draw_hand()

def main():
    game = Game()
    round_number = 1
    
    while True:
        print("\n" + "="*50)
        print(f"Round {round_number}")
        print(f"Total Score: {game.score}")
        print(f"Round Score: {game.round_score}")
        print(f"Plays remaining this round: {game.plays_remaining}")
        print(f"Discard actions remaining: {game.discards_remaining}")
        print("\nYour hand (8 cards):")
        for i, card in enumerate(game.hand):
            print(f"{i}: {card}")
        
        if game.plays_remaining == 0 and game.discards_remaining == 0:
            print(f"\nRound {round_number} complete!")
            print(f"Round score: {game.round_score}")
            input("Press Enter to start next round...")
            game.score += game.round_score
            game.start_new_round()
            round_number += 1
            continue

        options = []
        if game.plays_remaining > 0:
            options.append(f"1. Play hand (1-5 cards) [{game.plays_remaining} plays left]")
        if game.discards_remaining > 0:
            options.append(f"2. Discard cards (up to {MAX_DISCARDS} cards) [{game.discards_remaining} discards left]")
        options.append("3. View hand multipliers")
        options.append(f"4. Toggle sort ({('Rank' if game.sort_by_rank else 'Suit')} → {('Suit' if game.sort_by_rank else 'Rank')})")
        options.append("5. Quit game")
        
        action = input("\nChoose action:\n" + "\n".join(options) + "\n> ")

        if action == "1" and game.plays_remaining > 0:
            while True:
                try:
                    indices = input(f"Select 1-5 cards to play (enter numbers separated by spaces, 0-{HAND_SIZE-1}): ").split()
                    if len(indices) < 1:
                        print("You must play at least 1 card!")
                        continue
                    if len(indices) > 5:
                        print("You can't play more than 5 cards!")
                        continue
                    indices = [int(i) for i in indices]
                    if not all(0 <= i < len(game.hand) for i in indices):
                        print(f"Invalid card indices! Please use numbers 0-{HAND_SIZE-1}.")
                        continue
                    if len(set(indices)) != len(indices):
                        print("Please select different cards!")
                        continue
                    
                    selected_cards = [game.hand[i] for i in indices]
                    hand_type, base_points = game.evaluate_hand(selected_cards)
                    multiplier = game.get_hand_multiplier(hand_type)
                    points = int(base_points * multiplier)
                    game.round_score += points
                    game.plays_remaining -= 1
                    game.hand_counts[hand_type] += 1
                    
                    print(f"\nPlayed {hand_type.value}!")
                    print(f"Base points: {base_points}")
                    print(f"Multiplier: {multiplier:.1f}x")
                    print(f"Total points: {points}")
                    print(f"\nPlays remaining: {game.plays_remaining}")
                    break
                except ValueError:
                    print("Invalid input! Please enter numbers separated by spaces.")
        
        elif action == "2" and game.discards_remaining > 0:
            try:
                indices = input(f"Select up to {MAX_DISCARDS} cards to discard (space-separated numbers): ").split()
                indices = [int(i) for i in indices]
                
                if not all(0 <= i < len(game.hand) for i in indices):
                    print(f"Invalid card indices! Please use numbers 0-{HAND_SIZE-1}.")
                    continue
                    
                if not game.discard_cards(indices):
                    print(f"Can't discard {len(indices)} cards! Maximum is {MAX_DISCARDS} cards per action.")
                    continue
                    
                print(f"Discarded {len(indices)} cards.")
                print(f"\nPlays remaining: {game.plays_remaining}")
                print(f"Discard actions remaining: {game.discards_remaining}")
                
            except ValueError:
                print("Invalid input! Please enter numbers separated by spaces.")
        
        elif action == "3":  # View multipliers
            print("\nHand Multipliers:")
            for hand_type in HandType:
                plays = game.hand_counts[hand_type]
                multiplier = game.get_hand_multiplier(hand_type)
                print(f"{hand_type.value}: {multiplier:.1f}x (played {plays} times)")

        elif action == "4":  # Toggle sort
            game.sort_by_rank = not game.sort_by_rank
            game.sort_hand()
            print(f"\nSorting cards by {'rank' if game.sort_by_rank else 'suit'}")
            
        elif action == "5":  # Quit
            print(f"\nGame Over!")
            print(f"Final score: {game.score + game.round_score}")
            print(f"Rounds completed: {round_number - 1}")
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()