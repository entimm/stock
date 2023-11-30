from datetime import datetime


def row2info(row):
    info = {
        'name': row['stock_chi_name'],
        'symbol': row['symbol'][0: -3],
        'limited_freq': f"{row['m_days_n_boards_days']}天{row['m_days_n_boards_days']}板" if row['m_days_n_boards_boards'] else '首板',
        'turnover_ratio': round(row['turnover_ratio'] * 100, 2),
        'break_times': row.get('break_limit_up_times', '-'),
        'first_limit_up': row.get('first_limit_up', '-'),
        'last_limit_up': row.get('last_limit_up', '-'),
        'listed_date': row.get('listed_date', '-'),
        'flow_capital': row.get('non_restricted_capital', '-'),
        'buy_lock_volume_ratio': row.get('buy_lock_volume_ratio', '-'),
        'reason': f"{row.get('surge_reason.stock_reason', '-')}",
    }
    if info['first_limit_up'] != '-':
        info['first_limit_up'] = datetime.fromtimestamp(info['first_limit_up']).strftime('%Y-%m-%d %H:%M:%S')
    if info['last_limit_up'] != '-':
        info['last_limit_up'] = datetime.fromtimestamp(info['last_limit_up']).strftime('%Y-%m-%d %H:%M:%S')
    if info['listed_date'] != '-':
        info['listed_date'] = datetime.fromtimestamp(info['listed_date']).strftime('%Y-%m-%d')
    if info['flow_capital'] != '-':
        info['flow_capital'] = f"{round(info['flow_capital'] / 100000000, 2)}亿"

    return info
