import pandas as pd
import numpy as np
import os
import re
import difflib
import scipy.stats as stats

def greedy_splitter(text):
    if pd.isna(text):
        return []
    text = str(text)
    pattern = r'[\n\r/]+|(?<=\.)\s+-\s+'
    parts = re.split(pattern, text)
    return [p.strip() for p in parts if len(p.strip()) > 3]

def find_best_match(ans, choices, threshold=0.80):
    best_ratio = 0.0
    best_choice = None
    for choice in choices:
        ratio = difflib.SequenceMatcher(None, ans, choice).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_choice = choice
    if best_ratio >= threshold:
        return best_choice, best_ratio
    return None, 0.0

def ingest_and_unify_lonza(path_wooclap, path_scores):
    """
    Ingests and unifies Wooclap and Scores datasets.
    Uses difflib fuzzy matching for package-less compatibility.
    """
    if not os.path.exists(path_wooclap) or not os.path.exists(path_scores):
        raise FileNotFoundError("Lonza data files not found at specified paths.")
        
    df_wooclap = pd.read_csv(path_wooclap)
    df_scores = pd.read_csv(path_scores)
    
    # Melt Wooclap
    q_cols = [c for c in df_wooclap.columns if c.startswith('Q')]
    df_long = df_wooclap.melt(id_vars=['Username'], value_vars=q_cols, var_name='Question_Col', value_name='User_Answer')
    df_long['Question_ID'] = df_long['Question_Col'].str.extract(r'(Q\d+)')
    
    df_long['Split_Answers'] = df_long['User_Answer'].apply(greedy_splitter)
    df_exploded = df_long.explode('Split_Answers').dropna(subset=['Split_Answers']).copy()
    
    # Match Key
    if 'Match_Key' not in df_scores.columns:
        df_scores['Match_Key'] = df_scores['Translated_Text'].fillna(df_scores['Original_Text']).astype(str)
        
    matches = []
    for qid in df_exploded['Question_ID'].unique():
        subset_answers = df_exploded[df_exploded['Question_ID'] == qid]['Split_Answers'].unique()
        choices = df_scores[df_scores['Source_File'] == qid]['Match_Key'].unique()
        
        if len(choices) > 0:
            for ans in subset_answers:
                choice, score = find_best_match(ans, choices, threshold=0.75)
                if choice:
                    matches.append({
                        'Question_ID': qid,
                        'Split_Answers': ans,
                        'Matched_Text': choice
                    })
                    
    if not matches:
        raise ValueError("No fuzzy matches found between Wooclap and Scores.")
        
    df_matches = pd.DataFrame(matches)
    df_unified = df_exploded.merge(df_matches, on=['Question_ID', 'Split_Answers'], how='inner')
    
    df_unified = df_unified.merge(
        df_scores[['Source_File', 'Match_Key', 'Votes', 'Category']],
        left_on=['Question_ID', 'Matched_Text'],
        right_on=['Source_File', 'Match_Key'],
        how='left'
    )
    
    # Classify Sub_Question
    def classify_sub_question(row):
        cat = str(row['Category']).lower()
        qid = row['Question_ID']
        if qid == 'Q6':
            if 'like' in cat: return 'Positive'
            elif 'dislike' in cat or 'change' in cat: return 'Critique'
            elif 'use' in cat: return 'Context'
        elif qid == 'Q7':
            if 'change' in cat: return 'Critique'
            elif 'use' in cat: return 'Context'
        return 'Other'
        
    df_unified['Sub_Question'] = df_unified.apply(classify_sub_question, axis=1)
    df_unified = df_unified.drop_duplicates(subset=['Username', 'Matched_Text'])
    
    # Calculate User Prior (Average vote count for that user excluding current row)
    user_priors = []
    for idx, row in df_unified.iterrows():
        user = row['Username']
        # Leave-One-Out
        other_votes = df_unified[(df_unified['Username'] == user) & (df_unified.index != idx)]['Votes']
        if not other_votes.empty:
            prior = other_votes.mean()
        else:
            prior = df_unified['Votes'].mean()
        user_priors.append(prior)
    df_unified['User_Prior'] = user_priors
    
    return df_unified

def calculate_correlations_and_ttests(df_game):
    """
    Computes Pearson correlations and T-test for Phase 1 vs Phase 2 groups.
    Phase 1: Baseline (Control Group: ai_used == False)
    Phase 2: Cognitive Forcing Function (Treatment Group: ai_used == True)
    """
    if 'round_duration_seconds' not in df_game.columns or 'seq_score' not in df_game.columns:
        return {}
        
    # Aggregate to participant level for robust correlations
    user_agg = df_game.groupby('prolific_id').agg({
        'ai_used': 'mean', # AI Usage Score
        'round_duration_seconds': 'mean', # Task Duration
        'seq_score': 'mean', # Perceived effort / Difficulty
        'text_len': 'mean' # Text length
    }).reset_index()
    
    # Calculate Pearson r and p-value
    r_dur, p_dur = stats.pearsonr(user_agg['ai_used'], user_agg['round_duration_seconds'])
    r_eff, p_eff = stats.pearsonr(user_agg['ai_used'], user_agg['seq_score'])
    r_len, p_len = stats.pearsonr(user_agg['ai_used'], user_agg['text_len'])
    
    # 2. Two-tailed Independent T-Test
    # Phase 1: ai_used == False
    # Phase 2: ai_used == True
    g1_dur = df_game[df_game['ai_used'] == False]['round_duration_seconds']
    g2_dur = df_game[df_game['ai_used'] == True]['round_duration_seconds']
    
    t_dur, p_val_dur = stats.ttest_ind(g2_dur, g1_dur, equal_var=False)
    
    g1_eff = df_game[df_game['ai_used'] == False]['seq_score']
    g2_eff = df_game[df_game['ai_used'] == True]['seq_score']
    
    t_eff, p_val_eff = stats.ttest_ind(g2_eff, g1_eff, equal_var=False)
    
    # Alternate CFF contrast: edited suggestions (active CFF) vs passive AI copy-pasting
    # Phase 1 alt: ai_used == True & text_changed == False (Passive)
    # Phase 2 alt: ai_used == True & text_changed == True (Active CFF)
    g1_alt = df_game[(df_game['ai_used'] == True) & (df_game['text_changed'] == False)]['round_duration_seconds']
    g2_alt = df_game[(df_game['ai_used'] == True) & (df_game['text_changed'] == True)]['round_duration_seconds']
    
    t_alt, p_val_alt = stats.ttest_ind(g2_alt, g1_alt, equal_var=False)
    
    return {
        "corr_duration_r": float(r_dur),
        "corr_duration_p": float(p_dur),
        "corr_effort_r": float(r_eff),
        "corr_effort_p": float(p_eff),
        "corr_length_r": float(r_len),
        "corr_length_p": float(p_len),
        "ttest_duration_t": float(t_dur),
        "ttest_duration_p": float(p_val_dur),
        "ttest_effort_t": float(t_eff),
        "ttest_effort_p": float(p_val_eff),
        "ttest_alt_t": float(t_alt),
        "ttest_alt_p": float(p_val_alt),
        "user_agg": user_agg
    }

def simple_tfidf(texts, max_features=8):
    """
    Custom lightweight TF-IDF generator using only numpy and re.
    """
    stopwords = {'and', 'the', 'for', 'with', 'this', 'that', 'are', 'was', 'about', 'from', 'but', 'not'}
    word_doc_freq = {}
    doc_words = []
    for text in texts:
        words = [w.lower() for w in re.findall(r'[a-zA-Z]{3,}', str(text)) if w.lower() not in stopwords]
        doc_words.append(words)
        unique_words = set(words)
        for w in unique_words:
            word_doc_freq[w] = word_doc_freq.get(w, 0) + 1
            
    # Sort and pick top words
    top_words = sorted(word_doc_freq.keys(), key=lambda w: word_doc_freq[w], reverse=True)[:max_features]
    
    N = len(texts)
    features = {}
    for w in top_words:
        df = word_doc_freq[w]
        idf = np.log((1 + N) / (1 + df)) + 1
        tfidf_vals = []
        for doc in doc_words:
            tf = doc.count(w)
            tfidf_vals.append(tf * idf)
        features[f"text_{w}"] = tfidf_vals
        
    return pd.DataFrame(features)

def fit_ridge_coeffs(X_df, y_series, alpha=1.0):
    """
    Linear Ridge regression implementation using raw numpy solver.
    """
    X_mat = X_df.values
    y_mat = y_series.values
    
    # Add intercept column
    intercept = np.ones((X_mat.shape[0], 1))
    X_mat_bias = np.hstack([intercept, X_mat])
    
    n_features = X_mat_bias.shape[1]
    I = np.eye(n_features)
    I[0, 0] = 0.0 # Don't regularize intercept
    
    try:
        coefs = np.linalg.solve(X_mat_bias.T @ X_mat_bias + alpha * I, X_mat_bias.T @ y_mat)
        return coefs[1:]
    except np.linalg.LinAlgError:
        coefs = np.linalg.pinv(X_mat_bias.T @ X_mat_bias + alpha * I) @ X_mat_bias.T @ y_mat
        return coefs[1:]

def pre_render_bootstrap_importance(df_unified, num_iterations=400):
    """
    Resamples unified Lonza dataset via bootstrapping to compute feature importance.
    Pre-renders for standard confidence thresholds [0.80, 0.85, 0.90, 0.95, 0.99] to prevent slider lag.
    """
    # Align indices to prevent NaN during concat
    df_unified = df_unified.reset_index(drop=True)
    
    # 1. Feature Engineering
    texts = df_unified['Matched_Text'].fillna('').astype(str)
    X_tfidf = simple_tfidf(texts, max_features=8)
    
    # Metadata Dummies
    X_meta = pd.get_dummies(df_unified['Sub_Question'], prefix='SubQ', drop_first=False)
    X_meta = X_meta.astype(float)
    
    X_prior = pd.DataFrame({'User_Prior': df_unified['User_Prior']})
    
    X = pd.concat([X_prior, X_meta, X_tfidf], axis=1)
    y = df_unified['Votes'].fillna(0.0)
    
    features = X.columns.tolist()
    
    # 2. Bootstrapping
    coefficients = []
    np.random.seed(42)
    n_samples = len(X)
    
    for _ in range(num_iterations):
        indices = np.random.choice(n_samples, size=n_samples, replace=True)
        X_resampled = X.iloc[indices]
        y_resampled = y.iloc[indices]
        
        # Fit Ridge regression using numpy solver
        coefs = fit_ridge_coeffs(X_resampled, y_resampled, alpha=1.0)
        coefficients.append(coefs)
        
    coefficients = np.array(coefficients)
    
    # 3. Pre-render calculations for confidence intervals
    pre_rendered_data = {}
    confidence_levels = [0.80, 0.85, 0.90, 0.95, 0.99]
    
    means = np.mean(coefficients, axis=0)
    
    for cl in confidence_levels:
        lower_percentile = (1 - cl) / 2 * 100
        upper_percentile = (1 + cl) / 2 * 100
        
        lowers = np.percentile(coefficients, lower_percentile, axis=0)
        uppers = np.percentile(coefficients, upper_percentile, axis=0)
        
        features_stats = []
        for i, feat in enumerate(features):
            features_stats.append({
                "feature": feat,
                "mean": float(means[i]),
                "lower": float(lowers[i]),
                "upper": float(uppers[i]),
                "err_minus": float(means[i] - lowers[i]),
                "err_plus": float(uppers[i] - means[i])
            })
            
        pre_rendered_data[cl] = features_stats
        
    return pre_rendered_data

if __name__ == "__main__":
    w_path = r"c:\Users\maria\Documents\GitHub\fermentation_game\Tests\Lonza_Wooclap.csv"
    s_path = r"c:\Users\maria\Documents\GitHub\fermentation_game\Tests\Lonza_Scores.csv"
    game_path = r"c:\Users\maria\Documents\GitHub\fermentation_game\game_logs_fallback.csv"
    
    print("Testing data ingestion...")
    df_uni = ingest_and_unify_lonza(w_path, s_path)
    print(f"Unified table has {len(df_uni)} rows.")
    
    print("\nTesting bootstrap pre-rendering...")
    bootstrap_data = pre_render_bootstrap_importance(df_uni)
    print(f"Pre-rendered confidence interval structures for: {list(bootstrap_data.keys())}")
    print("Top feature metrics (95% CI):")
    for feat_stat in bootstrap_data[0.95][:3]:
        print(f"  {feat_stat['feature']}: Mean={feat_stat['mean']:.4f}, [{feat_stat['lower']:.4f}, {feat_stat['upper']:.4f}]")
        
    print("\nTesting correlations & t-tests...")
    df_g = pd.read_csv(game_path, on_bad_lines='skip')
    df_g['text_len'] = df_g['assessment'].fillna('').astype(str).apply(len)
    
    # Process timestamps to get round_duration_seconds
    df_g['timestamp'] = pd.to_datetime(df_g['timestamp'], errors='coerce')
    df_g = df_g.sort_values(['prolific_id', 'timestamp'])
    df_g['time_diff'] = df_g.groupby('prolific_id')['timestamp'].diff().dt.total_seconds().fillna(0.0)
    df_g['round_duration_seconds'] = df_g['time_diff'].apply(lambda x: x if 0 < x < 3600 else 25.0)
    
    df_g['seq_score'] = pd.to_numeric(df_g['seq_score'], errors='coerce').fillna(3.0)
    
    # Handle boolean column types
    df_g['ai_used'] = df_g['ai_used'].astype(str).map({'True': True, 'False': False, 'true': True, 'false': False}).fillna(False)
    df_g['text_changed'] = df_g['text_changed'].astype(str).map({'True': True, 'False': False, 'true': True, 'false': False}).fillna(False)
    
    stats_out = calculate_correlations_and_ttests(df_g)
    print(f"Correlation Duration vs AI: r={stats_out.get('corr_duration_r'):.4f}, p={stats_out.get('corr_duration_p'):.4f}")
    print(f"T-test Duration (AI vs No AI): t={stats_out.get('ttest_duration_t'):.4f}, p={stats_out.get('ttest_duration_p'):.4f}")
    print(f"T-test Duration (Active vs Passive AI CFF): t={stats_out.get('ttest_alt_t'):.4f}, p={stats_out.get('ttest_alt_p'):.4f}")
