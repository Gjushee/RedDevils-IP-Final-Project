from graphviz import Digraph

dot = Digraph(
    'ERD',
    graph_attr={
        'rankdir':  'LR',
        'splines':  'ortho',
        'nodesep':  '0.7',
        'ranksep':  '1.4',
        'fontname': 'Helvetica',
        'bgcolor':  '#f5f5f5',
    },
    node_attr={
        'shape':    'record',
        'fontname': 'Helvetica',
        'fontsize': '10',
        'style':    'filled',
    },
    edge_attr={
        'fontname':  'Helvetica',
        'fontsize':  '9',
        'color':     '#555555',
        'arrowhead': 'vee',
    }
)

# ── helper ────────────────────────────────────────────────────────────────────
def model(name, fields, fill):
    rows = '\\l'.join(fields) + '\\l'
    return f'{{{name}|{rows}}}'

# ── Django Auth ───────────────────────────────────────────────────────────────
with dot.subgraph(name='cluster_auth') as c:
    c.attr(label='Django Auth', style='filled', fillcolor='#dfe6e9', color='#b2bec3')
    c.node('User', model('User', ['PK  id', 'username', 'email', 'password'], '#ecf0f1'), fillcolor='#ecf0f1')

# ── register ──────────────────────────────────────────────────────────────────
with dot.subgraph(name='cluster_register') as c:
    c.attr(label='register', style='filled', fillcolor='#ffeaa7', color='#fdcb6e')
    c.node('Profile', model('Profile', ['PK  id', 'FK  user → User', 'role', 'full_name', 'email_verified'], '#fffde7'), fillcolor='#fffde7')

# ── catalogue ─────────────────────────────────────────────────────────────────
with dot.subgraph(name='cluster_catalogue') as c:
    c.attr(label='catalogue', style='filled', fillcolor='#d6eaf8', color='#85c1e9')
    fill = '#eaf4fb'
    c.node('Category',     model('Category',     ['PK  id', 'name', 'slug'], fill), fillcolor=fill)
    c.node('SubCategory',  model('SubCategory',  ['PK  id', 'FK  category', 'name'], fill), fillcolor=fill)
    c.node('Player',       model('Player',       ['PK  id', 'name', 'position', 'squad_number'], fill), fillcolor=fill)
    c.node('Product',      model('Product',      ['PK  id', 'FK  subcategory', 'FK  player', 'name', 'price', 'access_level', 'stock_quantity'], fill), fillcolor=fill)
    c.node('ProductImage', model('ProductImage', ['PK  id', 'FK  product', 'image', 'is_primary'], fill), fillcolor=fill)
    c.node('ProductRating',model('ProductRating',['PK  id', 'FK  user', 'FK  product', 'rating (1-5)'], fill), fillcolor=fill)

# ── transfers ─────────────────────────────────────────────────────────────────
with dot.subgraph(name='cluster_transfers') as c:
    c.attr(label='transfers', style='filled', fillcolor='#d5f5e3', color='#82e0aa')
    c.node('TransferRumour', model('TransferRumour', ['PK  id', 'FK  submitted_by → User', 'player_name', 'current_club', 'status', 'likelihood'], '#eafaf1'), fillcolor='#eafaf1')

# ── cart ──────────────────────────────────────────────────────────────────────
with dot.subgraph(name='cluster_cart') as c:
    c.attr(label='cart', style='filled', fillcolor='#ebdef0', color='#c39bd3')
    fill = '#f5eef8'
    c.node('Cart',         model('Cart',         ['PK  id', 'FK  user → User'], fill), fillcolor=fill)
    c.node('CartItem',     model('CartItem',     ['PK  id', 'FK  cart', 'FK  product', 'quantity', 'size'], fill), fillcolor=fill)
    c.node('WishlistItem', model('WishlistItem', ['PK  id', 'FK  user → User', 'FK  product'], fill), fillcolor=fill)

# ── checkout ──────────────────────────────────────────────────────────────────
with dot.subgraph(name='cluster_checkout') as c:
    c.attr(label='checkout', style='filled', fillcolor='#fce4ec', color='#f48fb1')
    fill = '#fff0f5'
    c.node('Order',     model('Order',     ['PK  id', 'FK  user → User', 'order_ref', 'status', 'total_amount'], fill), fillcolor=fill)
    c.node('OrderItem', model('OrderItem', ['PK  id', 'FK  order', 'product_name', 'quantity', 'unit_price'], fill), fillcolor=fill)

# ── gold_hub ──────────────────────────────────────────────────────────────────
with dot.subgraph(name='cluster_gold_hub') as c:
    c.attr(label='gold_hub', style='filled', fillcolor='#fff3cd', color='#ffc107')
    fill = '#fffde7'
    c.node('Poll',       model('Poll',       ['PK  id', 'title', 'month_label', 'is_active'], fill), fillcolor=fill)
    c.node('PollOption', model('PollOption', ['PK  id', 'FK  poll', 'player_name', 'order'], fill), fillcolor=fill)
    c.node('Vote',       model('Vote',       ['PK  id', 'FK  user → User', 'FK  poll', 'FK  option'], fill), fillcolor=fill)
    c.node('PlayerStat', model('PlayerStat', ['PK  id', 'name', 'position', 'season', 'goals', 'assists', 'rating'], fill), fillcolor=fill)
    c.node('ClubStat',   model('ClubStat',   ['PK  id', 'season', 'competition', 'played', 'won', 'is_current'], fill), fillcolor=fill)

# ── relationships ─────────────────────────────────────────────────────────────
# register
dot.edge('Profile', 'User', label='1:1')

# catalogue
dot.edge('SubCategory',   'Category')
dot.edge('Product',       'SubCategory')
dot.edge('Product',       'Player')
dot.edge('ProductImage',  'Product')
dot.edge('ProductRating', 'Product')
dot.edge('ProductRating', 'User')

# transfers
dot.edge('TransferRumour', 'User')

# cart
dot.edge('Cart',         'User')
dot.edge('CartItem',     'Cart')
dot.edge('CartItem',     'Product')
dot.edge('WishlistItem', 'User')
dot.edge('WishlistItem', 'Product')

# checkout
dot.edge('Order',     'User')
dot.edge('OrderItem', 'Order')

# gold_hub
dot.edge('PollOption', 'Poll')
dot.edge('Vote',       'Poll')
dot.edge('Vote',       'PollOption')
dot.edge('Vote',       'User')

# ── render ────────────────────────────────────────────────────────────────────
dot.render('erd', format='png', cleanup=True)
print('Saved → erd.png')
