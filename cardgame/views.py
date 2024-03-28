
# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Card, Player, Game,Hand
from django.contrib import messages

def home(request):
    return render(request, 'cardgame/home.html')

def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email = request.POST.get('email')

        # Check if any of the required fields are empty
        if not username or not password1 or not password2 or not email:
            return render(request, 'cardgame/signup.html', {'error': 'All fields are required.'})

        # Check if passwords match
        if password1 != password2:
            return render(request, 'cardgame/signup.html', {'error': 'Passwords do not match.'})

        # Check if the username is already taken
        if User.objects.filter(username=username).exists():
            return render(request, 'cardgame/signup.html', {'error': 'Username is already taken.'})

        # Create the user and player
        user = User.objects.create_user(username, email, password1)
        Player.objects.create(user=user)

        # Log in the user
        login(request, user)
        # messages.success(request, 'Your account has been successfully created!')
        return redirect('play_game')

    return render(request, 'cardgame/signup.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if username and password are provided
        if not username or not password:
            return render(request, 'cardgame/login.html', {'error': 'Username and password are required.'})

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log in the user
            login(request, user)
            return render(request, 'cardgame/play_game.html')
        else:
            return render(request, 'cardgame/login.html', {'error': 'Invalid login credentials.'})

    return render(request, 'cardgame/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def play_game(request):
    user = request.user
    player, created = Player.objects.get_or_create(user=user)
    game, created = Game.objects.get_or_create()
    
    if game.current_player is None:
        game.current_player = player
        game.save()

    # Check if it's the current player's turn
    if game.current_player != player:
        messages.error(request, "It's not your turn.")
        return redirect('home')  # Redirect to home or another appropriate page

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'see':
            see_action(request, game.id, player)
        elif action == 'raise':
            raise_action(request, game.id)
        elif action == 'fold':
            fold_action(request, game.id, player)
        elif action == 'showdown':
            showdown(request, game, player)

        # Switch to the next player's turn
        switch_turn(game)    

    context = {'game': game, 'player': player}
    
    if player == game.current_player:
        # It's the current player's turn
        return render(request, 'cardgame/play_game.html', context)
    else:
        # Wait for other players' turns
        return render(request, 'cardgame/wait_for_turn.html', context)

@login_required
def switch_turn(request, game_id):
    game = Game.objects.get(pk=game_id)

    if game.current_player is not None:
        # Switch to the next player's turn
        players = Player.objects.all()
        current_index = players.index(game.current_player)
        next_index = (current_index + 1) % len(players)
        game.current_player = players[next_index]
        game.save()

    return JsonResponse({'status': 'success', 'current_player': game.current_player.user.username})

@login_required
def bet(request, game_id):
    game = Game.objects.get(pk=game_id)
    bet_amount = int(request.POST.get('bet_amount', 0))

    if bet_amount <= 0:
        return JsonResponse({'status': 'error', 'message': 'Invalid bet amount'})

    player = request.user.player

    # Update player's wallet and game pot based on the bet amount
    if player.wallet >= bet_amount:
        player.wallet -= bet_amount
        player.save()
        game.pot += bet_amount
        game.save()
    else:
        return JsonResponse({'status': 'error', 'message': 'Insufficient funds'})

    # Add logic for updating the current player, switching turns, etc.
    # (This will depend on your specific game rules)

    return JsonResponse({'status': 'success', 'pot': game.pot, 'wallet': player.wallet, 'current_player': game.current_player.user.username})


@login_required
def showdown(request, game_id):
    game = Game.objects.get(pk=game_id)

    # Ensure there are more than one player in the game
    if game.current_player is not None and Player.objects.count() > 1:
        players = Player.objects.all()
        # Get the hands of all players
        hands = [Hand.objects.get(player=player) for player in players]

        # Compare hands and determine the winner
        winner_index = compare_hands(hands)

        if winner_index is not None:
            winner = players[winner_index]
            winner.wallet += game.pot
            winner.save()
            messages.success(request, f'Congratulations! {winner.user.username} won the pot.')
        else:
            messages.info(request, 'It\'s a draw! The pot will be carried over to the next round.')

        # Reset game state for the next round
        game.pot = 0
        game.current_player = None
        game.save()

        return JsonResponse({'status': 'success', 'winner': winner.user.username if winner_index is not None else None})
    else:
        return JsonResponse({'status': 'error', 'message': 'Not enough players for a showdown.'})

def compare_hands(player1, player2):
    # Implement hand comparison logic here
    # Return a positive value if player1 has a better hand, negative if player2 is better, and 0 if hands are equal

    # Example: Check for Pure Sequence
    if is_pure_sequence(player1.cards):
        return 1
    elif is_pure_sequence(player2.cards):
        return -1

    # Add more logic for other hand rankings: Sequence, Flush, Pair, High Card
    # ...

    return 0


def determine_winner(game):
    players = Player.objects.all()

    # Get hands of all players
    hands = {player: get_hand(player) for player in players}

    # Determine the winner based on hand comparison
    winner = max(hands, key=lambda player: hands[player])

    return winner
def get_hand(player):
    # Implement logic to determine the type of hand
    # Example: Check for Trail, Pure Sequence, Sequence, Flush, Pair, High Card, etc.
    # Return a value representing the hand type
    # (e.g., 1 for Trail, 2 for Pure Sequence, 3 for Sequence, etc.)
    # Add more cases as needed
    if is_trail(player):
        return 1
    elif is_pure_sequence(player):
        return 2
    elif is_sequence(player):
        return 3
    elif is_flush(player):
        return 4
    elif is_pair(player):
        return 5
    else:
        return 6 
    
def is_trail(player):
    # Implement logic to check for Trail
    # Return True if the player has a Trail, False otherwise
    # Example: Check if all three cards have the same rank
    cards = player.cards.all()
    return len(set(card.rank for card in cards)) == 1    

def is_pure_sequence(cards):
    # Sort cards by rank
    sorted_cards = sorted(cards, key=lambda card: card.rank)
    first_suit = sorted_cards[0].suit
    # Check if cards form a Pure Sequence
    for i in range(1, len(sorted_cards)):
        if sorted_cards[i].rank - sorted_cards[i - 1].rank != 1 or sorted_cards[i].suit != first_suit:
            return False
    return True

def is_sequence(player):
    # Implement logic to check for Sequence
    # Return True if the player has a Sequence, False otherwise
    # Example: Check if the cards are in consecutive order
    cards = sorted(player.cards.all(), key=lambda card: card.rank)
    for i in range(len(cards) - 1):
        if cards[i + 1].rank - cards[i].rank != 1:
            return False
    return True

def is_flush(player):
    # Implement logic to check for Flush
    # Return True if the player has a Flush, False otherwise
    # Example: Check if all cards are of the same suit
    cards = player.cards.all()
    return len(set(card.suit for card in cards)) == 1

def is_pair(player):
    # Implement logic to check for Pair
    # Return True if the player has a Pair, False otherwise
    # Example: Check if there are two cards with the same rank
    cards = player.cards.all()
    rank_counts = {}
    for card in cards:
        rank_counts[card.rank] = rank_counts.get(card.rank, 0) + 1
    return any(count == 2 for count in rank_counts.values())

@login_required
def see_action(request, game_id, player):
    game = Game.objects.get(pk=game_id)
    player = request.user.player
    # Implement logic for "See" action
    # Example: Player matches the current bet in the pot
    if player.wallet >= game.pot:
        player.wallet -= game.pot
        game.pot *= 2  # Double the pot amount for simplicity
        player.save()
        game.save()
        return JsonResponse({'status': 'success', 'message': 'You have seen the bet.', 'pot': game.pot, 'wallet': player.wallet})
    else:
        return JsonResponse({'status': 'error', 'message': 'Not enough money to see the bet.'})

@login_required
def raise_action(request, game_id):
    game = Game.objects.get(pk=game_id)
    player = request.user.player

    # Implement logic for "Raise" action
    # Example: Player increases the current bet
    raise_amount = int(request.POST.get('raise_amount', 0))

    if raise_amount <= 0 or player.wallet < raise_amount:
        return JsonResponse({'status': 'error', 'message': 'Invalid raise amount or not enough money.'})

    player.wallet -= raise_amount
    game.pot += raise_amount
    player.save()
    game.save()

    return JsonResponse({'status': 'success', 'message': f'You have raised the bet by {raise_amount}.', 'pot': game.pot, 'wallet': player.wallet})


def fold_action(request, game_id):
    game = Game.objects.get(pk=game_id)
    player = request.user.player
    try:
        # Add the money in the pot back to the player's wallet
        player.wallet += game.pot
        player.save()

        # Set the current player to None to indicate fold
        game.current_player = None
        game.save()

        # Return a success response with a message and updated wallet amount
        return JsonResponse({'status': 'success', 'message': 'You have folded.', 'wallet': player.wallet})
    except Exception as e:
        # Handle any errors that occur during the fold action
        return JsonResponse({'status': 'error', 'message': 'An error occurred while processing your fold request.'})
