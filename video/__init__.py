def __init__(
    self,
    encoder="libx264",
    quality="High",
    progress_callback=None,
    log_callback=None
):

    self.encoder = encoder
    self.quality = quality
    self.progress_callback = progress_callback
    self.log_callback = log_callback