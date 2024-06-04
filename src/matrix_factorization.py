import numpy as np
import pandas as pd


def initialize_data(data:pd.DataFrame, num_factors: int = 5):
    """
    Loads the dataset from a CSV file and initializes user and book factor matrices.

    Args:
        filepath (str): Path to the CSV file containing the data.
        num_factors (int): Number of latent factors to use in the matrices.

    Returns:
        tuple: A tuple containing the dataset (DataFrame), user factors matrix (W),
               book factors matrix (Z), number of users, and number of books.
    """
    
    num_users = len(data["user_id"].unique())
    num_books = len(data["book_id"].unique())

    W = np.random.normal(scale=1.0 / num_factors, size=(num_users, num_factors))
    Z = np.random.normal(scale=1.0 / num_factors, size=(num_books, num_factors))

    return W, Z, num_users, num_books


def factorize_matrix_SGD(
    data: pd.DataFrame,
    W: np.ndarray,
    Z: np.ndarray,
    num_iterations: int = 100000,
    batch_size: int = 32,
    learning_rate: float = 0.01,
    lambda_reg: float = 0.01,
    log_every: int = 1000,

):
    """
    Performs stochastic gradient descent to optimize the factor matrices W and Z.

    Args:
        data (pd.DataFrame): Dataset containing user IDs, book IDs, and ratings.
        W (np.ndarray): User factors matrix.
        Z (np.ndarray): Book factors matrix.
        num_iterations (int): Number of iterations to run SGD.
        batch_size (int): Number of samples in each batch.
        learning_rate (float): Learning rate for updates.

    Returns:
        tuple: Updated user factors matrix (W) and book factors matrix (Z).
    """

    cumulative_loss = []
    for iteration in range(num_iterations):
        batch = data.sample(n=batch_size, replace=True)

        users = batch["user_id"].values - 1
        books = batch["book_id"].values - 1
        ratings = batch["rating"].values

        predictions = compute_predictions(batch, W, Z)
        errors = ratings - predictions

        for idx in range(batch_size):
            u = users[idx].astype(int)
            b = books[idx].astype(int)
            W_grad = errors[idx] * Z[b, :] - lambda_reg * W[u, :]
            Z_grad = errors[idx] * W[u, :] - lambda_reg * Z[b, :]
            W[u, :] += learning_rate * W_grad
            Z[b, :] += learning_rate * Z_grad

        cumulative_loss.append(np.mean(errors**2))
        if iteration % log_every == 0:
            print(f"Iteration: {iteration}, MSE: {np.mean(cumulative_loss)}")

    return W, Z


def compute_predictions(
    data: pd.DataFrame, W: np.ndarray, Z: np.ndarray
) -> pd.DataFrame:
    """
    Computes the predicted ratings for each user and book pair in the data.

    Args:
        data (pd.DataFrame): Dataset containing user IDs and book IDs for which we want to predict ratings.
        W (np.ndarray): User factors matrix.
        Z (np.ndarray): Book factors matrix.

    Returns:
        pd.DataFrame: Updated DataFrame including a new column with predicted ratings.
    """

    users = (data["user_id"].values - 1).astype(int)
    books = (data["book_id"].values - 1).astype(int)

    predictions = np.sum(W[users, :] * Z[books, :], axis=1)

    return predictions


def calculate_mse(labels, predictions) -> float:
    """
    Calculates the mean squared error (MSE) between actual and predicted ratings.

    Args:
        data (pd.DataFrame): DataFrame containing actual and predicted ratings.

    Returns:
        float: The calculated mean squared error.
    """
    mse = np.mean((labels - predictions) ** 2)
    return mse


if __name__ == "__main__":
    filepath = "data/ratings.csv"
    data, W, Z, num_users, num_books = initialize_data(filepath)
    W, Z = factorize_matrix_SGD(data, W, Z, num_iterations=10000, batch_size=1024)
    predictions = compute_predictions(data, W, Z)
    mse = calculate_mse(data["rating"], predictions)
    print(f"Mean Squared Error: {mse}")
