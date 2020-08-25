import numpy as np
import random
from typing import Tuple, List


class Augmenter:
    def __init__(
            self,
            logo_aug: list,
            image_aug: list,
            transp_thresh: float,
            transp_range: List[float]
    ):
        self.logo_transforms = logo_aug
        self.image_aug = image_aug
        self.trans_thresh = transp_thresh
        self.trans_min, self.trans_max = transp_range

    def generate_image(
            self,
            logo: np.ndarray,
            background: np.ndarray
    ) -> Tuple[np.ndarray, list, list]:
        """
        Applies transformations to the logo, overlays on top of the
        background and applies possible transformations to the entire image
        """
        log = list()
        background_size = background.shape[:2]

        # Apply transformations to the logo
        for logo_t in self.logo_transforms:
            if random.random() > logo_t.thresh:
                logo = logo_t(logo, background_size)
                log.append(logo_t.name)

        # Combine the logo and background
        combined, coord, transp_value = self._overlay_logo(logo, background)
        log.append(f"transp_value: {transp_value}")

        # Apply transformation to the entire image (blurring, noise etc)
        for image_t in self.image_aug:
            if random.random() > image_t.thresh:
                combined = image_t(combined)
                log.append(image_t.name)

        return combined, coord, log

    def _overlay_logo(
            self,
            logo: np.ndarray,
            background: np.ndarray
    ) -> Tuple[np.ndarray, list, float]:
        """ Overlays company's logo on top of the provided background """
        logo_h, logo_w = logo.shape[:2]
        backgr_h, backgr_w = background.shape[:2]
        allowed_range_x = backgr_w - int(logo_w * 1.05)
        allowed_range_y = backgr_h - int(logo_h * 1.05)

        # Pick logo location coordinates
        x1 = random.randint(1, allowed_range_x)
        y1 = random.randint(1, allowed_range_y)
        x2 = x1 + logo_w
        y2 = y1 + logo_h
        assert x1 < x2 and y1 < y2 and all((x1 > 0, x2 > 0, y1 > 0, y2 > 0))
        assert x2 < backgr_w and y2 < backgr_h

        # Pick transparency value
        trans_factor = 1.0
        if random.random() > self.trans_thresh:
            trans_factor = float(random.randint(
                int(self.trans_min * 100), int(self.trans_max * 100)
            ) / 100.0)
            assert 0.0 < trans_factor <= 1.0

        overlay = logo[..., :3]
        mask = (logo[..., 3:] / 255.0) * trans_factor
        background[y1:y2, x1:x2] = (1.0 - mask) * \
                                    background[y1:y2, x1:x2] + mask * overlay

        return background, [x1, y1, x2, y2], trans_factor
