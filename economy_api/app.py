from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import random2 as random
import json

app = Flask(__name__)
CORS(app)

user_coins = {}
transactions = []
daily_claims = {}
transaction_counter = 1

class Transaction:
    def __init__(self, trans_id, from_user, to_user, amount, trans_type, description=""):
        self.id = trans_id
        self.from_user = from_user
        self.to_user = to_user
        self.amount = amount
        self.type = trans_type
        self.description = description
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        return {
            'id': self.id,
            'from_user': self.from_user,
            'to_user': self.to_user,
            'amount': self.amount,
            'type': self.type,
            'description': self.description,
            'timestamp': self.timestamp
        }


def get_user_balance(user_id):
    return user_coins.get(user_id, 0)

def update_user_balance(user_id, amount):
    if user_id not in user_coins:
        user_coins[user_id] = 0
    user_coins[user_id] += amount
    return user_coins[user_id]

def can_claim_daily(user_id):
    if user_id not in daily_claims:
        return True
    
    last_claim = datetime.fromisoformat(daily_claims[user_id])
    now = datetime.now()
    return (now - last_claim).days >= 1

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'economy-api'}), 200

@app.route('/coin/get-daily', methods=['POST'])
def get_daily_coins():
    global transaction_counter
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        if not can_claim_daily(user_id):
            return jsonify({'error': 'Daily coins already claimed today'}), 400
        
        daily_amount = 100
        
        new_balance = update_user_balance(user_id, daily_amount)
        
        transaction = Transaction(
            trans_id=transaction_counter,
            from_user="system",
            to_user=user_id,
            amount=daily_amount,
            trans_type="daily",
            description="Daily coin claim"
        )
        transactions.append(transaction)
        transaction_counter += 1
        
        daily_claims[user_id] = datetime.now().isoformat()
        
        return jsonify({
            'message': 'Daily coins claimed successfully',
            'amount': daily_amount,
            'new_balance': new_balance,
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/coin/show', methods=['GET'])
def show_coins():
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id parameter'}), 400
        
        balance = get_user_balance(user_id)
        can_claim = can_claim_daily(user_id)
        
        return jsonify({
            'user_id': user_id,
            'balance': balance,
            'can_claim_daily': can_claim
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/coin/transfer', methods=['POST'])
def transfer_coins():
    global transaction_counter
    try:
        data = request.get_json()
        from_user = data.get('from_user')
        to_user = data.get('to_user')
        amount = float(data.get('amount', 0))
        
        if not all([from_user, to_user, amount]):
            return jsonify({'error': 'Missing required fields: from_user, to_user, amount'}), 400
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
        
        if from_user == to_user:
            return jsonify({'error': 'Cannot transfer to yourself'}), 400
        
        sender_balance = get_user_balance(from_user)
        if sender_balance < amount:
            return jsonify({'error': 'Insufficient balance'}), 400
        
        update_user_balance(from_user, -amount)
        update_user_balance(to_user, amount)
        
        transaction = Transaction(
            trans_id=transaction_counter,
            from_user=from_user,
            to_user=to_user,
            amount=amount,
            trans_type="transfer",
            description=f"Transfer from {from_user} to {to_user}"
        )
        transactions.append(transaction)
        transaction_counter += 1
        
        return jsonify({
            'message': 'Transfer completed successfully',
            'transaction': transaction.to_dict(),
            'sender_new_balance': get_user_balance(from_user),
            'receiver_new_balance': get_user_balance(to_user)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/coin/update', methods=['PUT'])
def update_coins():
    global transaction_counter
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        amount = float(data.get('amount', 0))
        reason = data.get('reason', 'Manual update')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        new_balance = update_user_balance(user_id, amount)
        
        transaction = Transaction(
            trans_id=transaction_counter,
            from_user="admin" if amount > 0 else user_id,
            to_user=user_id if amount > 0 else "admin",
            amount=abs(amount),
            trans_type="admin_update",
            description=reason
        )
        transactions.append(transaction)
        transaction_counter += 1
        
        return jsonify({
            'message': 'Balance updated successfully',
            'new_balance': new_balance,
            'transaction': transaction.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/coin/remove', methods=['DELETE'])
def remove_user():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        if user_id in user_coins:
            del user_coins[user_id]
        
        if user_id in daily_claims:
            del daily_claims[user_id]
        
        return jsonify({'message': f'User {user_id} removed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/airplane/distribute', methods=['POST'])
def airplane_distribute():
    """
    Airplane distribution - creates new coins and distributes among users
    """
    global transaction_counter
    try:
        data = request.get_json()
        total_amount = float(data.get('total_amount', 0))
        participants = data.get('participants', [])
        
        if total_amount <= 0:
            return jsonify({'error': 'Total amount must be positive'}), 400
        
        if len(participants) < 2:
            return jsonify({'error': 'Need at least 2 participants'}), 400
        
        distributions = []
        remaining_amount = total_amount
        
        for i, participant in enumerate(participants[:-1]):
            max_percentage = min(0.4, remaining_amount / total_amount)
            min_percentage = 0.05
            percentage = random.uniform(min_percentage, max_percentage)
            amount = round(remaining_amount * percentage, 2)
            
            distributions.append({
                'user_id': participant,
                'amount': amount
            })
            remaining_amount -= amount
        
        distributions.append({
            'user_id': participants[-1],
            'amount': round(remaining_amount, 2)
        })
        
        transaction_list = []
        for dist in distributions:
            update_user_balance(dist['user_id'], dist['amount'])
            
            transaction = Transaction(
                trans_id=transaction_counter,
                from_user="system",
                to_user=dist['user_id'],
                amount=dist['amount'],
                trans_type="airplane",
                description="Airplane distribution (minted coins)"
            )
            transactions.append(transaction)
            transaction_list.append(transaction.to_dict())
            transaction_counter += 1
        
        return jsonify({
            'message': 'Airplane distribution completed successfully',
            'total_distributed': total_amount,
            'distributions': distributions,
            'transactions': transaction_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/transactions', methods=['GET'])
def get_transactions():
    try:
        user_id = request.args.get('user_id')
        trans_type = request.args.get('type')
        limit = int(request.args.get('limit', 50))
        
        filtered_transactions = transactions
        
        if user_id:
            filtered_transactions = [t for t in filtered_transactions 
                                   if t.from_user == user_id or t.to_user == user_id]
        
        if trans_type:
            filtered_transactions = [t for t in filtered_transactions if t.type == trans_type]
        
        filtered_transactions.sort(key=lambda x: x.timestamp, reverse=True)
        filtered_transactions = filtered_transactions[:limit]
        
        return jsonify({
            'transactions': [t.to_dict() for t in filtered_transactions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    try:
        sorted_users = sorted(user_coins.items(), key=lambda x: x[1], reverse=True)
        
        leaderboard = []
        for rank, (user_id, balance) in enumerate(sorted_users[:10], 1):
            leaderboard.append({
                'rank': rank,
                'user_id': user_id,
                'balance': balance
            })
        
        return jsonify({'leaderboard': leaderboard}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

