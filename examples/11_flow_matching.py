"""Flow matching işareti ve episode maskesi: NumPy ile çözümlü hesap, model indirmez."""
import json
import numpy as np


def main():
    action = np.array([.2, -.4])
    noise = np.array([1., .6])
    t = .75
    x_t = (1 - t) * action + t * noise
    target_velocity = noise - action
    prediction = np.array([.7, 1.2])
    mse = np.mean((prediction - target_velocity) ** 2)
    x = noise.copy()
    path = [x.tolist()]
    for _ in range(4):
        x = x - .25 * target_velocity  # ideal constant field, NOT learned SmolVLA
        path.append(x.tolist())
    np.testing.assert_allclose(x, action, atol=1e-12)
    np.testing.assert_allclose(mse, .025, atol=1e-12)
    # B=1,H=3,D=2; final time point padded, despite enormous raw errors.
    squared_errors = np.array([[[1., 4.], [9., 16.], [1000., 1000.]]])
    is_pad = np.array([[False, False, True]])
    masked_sum = (squared_errors * (~is_pad)[..., None]).sum()
    correct = masked_sum / ((~is_pad).sum() * squared_errors.shape[-1])
    wrong = masked_sum / squared_errors.size
    assert correct == 7.5 and wrong == 5.0
    print(json.dumps({"action": action.tolist(), "noise": noise.tolist(), "t": t,
                      "x_t": x_t.tolist(), "target_velocity": target_velocity.tolist(),
                      "prediction_mse": float(mse), "ideal_euler_path": path,
                      "correct_masked_loss": float(correct), "wrong_full_size_loss": float(wrong),
                      "scope": "Arithmetic only; no pretrained model or learned velocity field"}, indent=2))


if __name__ == "__main__":
    main()
