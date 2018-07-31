"""Matchzoo point generator."""

import numpy as np
from matchzoo import engine
from matchzoo import tasks
from matchzoo.datapack import DataPack


class PointGenerator(engine.BaseGenerator):
    """PointGenerator for Matchzoo.

    Ponit generator can be used for classification as well as ranking.

    Examples:
        >>> data = [{
        ... 'text_left':[1,2],
        ... 'text_right': [3,4],
        ... 'label': 0,
        ... 'id': ('id0', 'id1')
        ... }]
        >>> input = DataPack(data)
        >>> task = tasks.Classification(num_classes=2)
        >>> from matchzoo.generators import PointGenerator
        >>> generator = PointGenerator(input, task, 1, True)
        >>> x, y = generator[0]

    """

    def __init__(
        self,
        inputs: DataPack,
        task: engine.BaseTask,
        batch_size: int=32,
        shuffle: bool=True
    ):
        """Initialize the point generator."""
        self._task = task
        transformed_inputs = self.transform_data(inputs)
        self.x_left, self.x_right, self.y, self.ids = transformed_inputs
        super(PointGenerator, self).__init__(batch_size,
                                             len(inputs.dataframe),
                                             shuffle
                                             )

    def transform_data(self, inputs: DataPack):
        """Obtain the transformed data from datapack."""
        data = inputs.dataframe
        x_left = np.asarray(data.text_left)
        x_right = np.asarray(data.text_right)
        y = np.asarray(data.label)
        ids = np.asarray(data.id)
        return x_left, x_right, y, ids

    def _get_batch_of_transformed_samples(self, index_array):
        """Get all a batch of samples."""
        batch_size = len(index_array)
        batch_x_left = []
        batch_x_right = []
        batch_ids = []
        if isinstance(self._task, tasks.Ranking):
            batch_y = self.y
        elif isinstance(self._task, tasks.Classification):
            batch_y = np.zeros((batch_size, self._task._num_classes),
                               dtype=np.int32)
            for i, label in enumerate(self.y[index_array]):
                batch_y[i, label] = 1
        else:
            raise ValueError('Error target mode in point generator.')

        for key, val in enumerate(index_array):
            batch_x_left.append(self.x_left[val])
            batch_x_right.append(self.x_right[val])
            batch_ids.append(self.ids[val])

        return ({'x_left': np.array(batch_x_left), 'x_right':
                 np.array(batch_x_right), 'ids':
                 batch_ids}, np.array(batch_y))
