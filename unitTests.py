import unittest
import numpy as np
import geometry

class TestGeometry(unittest.TestCase):
    def test_look_at_origin(self):
        eye = np.array([0,0,0])
        target = np.array([0,0,-1])
        up = np.array([0,1,0])
        result = geometry.get_look_at_matrix(eye, target, up)
        expected = np.array([
            [1, 0,  0, 0],
            [0, 1,  0, 0],
            [0, 0,  1, 0],
            [0, 0,  0, 1]
        ], dtype=np.float32)
        np.testing.assert_allclose(result, expected, rtol=1e-5, atol=1e-8)

    def test_look_at_translation(self):
        eye = np.array([0,0,5])
        target = np.array([0,0,0])
        up = np.array([0,1,0])
        result = geometry.get_look_at_matrix(eye, target, up)
        expected = np.array([
            [1, 0,  0, 0],
            [0, 1,  0, 0],
            [0, 0,  1, -5],
            [0, 0,  0, 1]
        ], dtype=np.float32)
        np.testing.assert_allclose(result, expected, rtol=1e-5, atol=1e-8)

    def test_look_at_rotation(self):
        eye = np.array([0,0,0])
        target = np.array([1,0,0])   # looking along +X
        up = np.array([0,1,0])

        result = geometry.get_look_at_matrix(eye,target,up)

        # forward becomes X axis → matrix should rotate world
        expected = np.array([
            [0,0,1,0],
            [0,1, 0,0],
            [-1,0, 0,0],
            [0,0, 0,1]
        ], dtype=np.float32)

        np.testing.assert_allclose(result, expected, rtol=1e-5, atol=1e-8)

    def test_base_ortogonality(self):

        eye = np.array([0,30,90])
        target = np.array([0,10,0])   
        up = np.array([0,1,0])

        result = geometry.get_look_at_matrix(eye,target,up)

        R = result[:3,:3]
        np.testing.assert_allclose(R @ R.T, np.eye(3), atol=1e-5)

    def test_normalize_coordinate(self):
        result = geometry.get_ndc(100,100)
        np.testing.assert_equal(result,1)

        result = geometry.get_ndc(50,100)
        np.testing.assert_equal(result,0)
    

if __name__ == '__main__':
    unittest.main()