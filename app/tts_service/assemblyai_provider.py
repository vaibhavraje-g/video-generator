"""AssemblyAI transcription provider using direct API calls"""

import os
import time
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class AssemblyAIProvider:
    """AssemblyAI transcription service provider using direct API calls"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize AssemblyAI provider

        Args:
            config: Configuration dictionary containing API settings
        """
        self.api_key = config.get("api_key") or os.getenv("assemblyai_authorization")
        if not self.api_key:
            logger.warning(
                "AssemblyAI API key not found. Local transcription will be used."
            )
            self.api_key = None

        self.base_url = "https://api.assemblyai.com/v2"
        self.headers = (
            {"authorization": self.api_key, "content-type": "application/json"}
            if self.api_key
            else {}
        )
        self.timeout = config.get("timeout", 30)
        self.max_retries = config.get("max_retries", 3)
        self.polling_interval = config.get("polling_interval", 3)

        if not config.get("enabled", True):
            logger.warning("AssemblyAI provider is disabled")

    def transcribe_audio_file(self, audio_file_path: str, **kwargs) -> str:
        """
        Transcribe audio file to text using AssemblyAI direct API calls

        Args:
            audio_file_path: Path to audio file
            **kwargs: Additional transcription parameters

        Returns:
            Transcribed text

        Raises:
            RuntimeError: If transcription fails
        """
        if not self.api_key:
            raise ValueError(
                "AssemblyAI API key not found. Set assemblyai_authorization environment variable."
            )

        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")

        try:
            # Upload audio file
            upload_url = f"{self.base_url}/upload"
            with open(audio_file_path, "rb") as audio_file:
                upload_response = requests.post(
                    upload_url,
                    headers={"authorization": self.api_key},
                    files={"file": audio_file},
                    timeout=self.timeout,
                )
            upload_response.raise_for_status()
            audio_url = upload_response.json()["upload_url"]

            # Start transcription
            transcript_url = f"{self.base_url}/transcript"
            transcript_data = {
                "audio_url": audio_url,
                "language_detection": kwargs.get("language_detection", True),
                "punctuation": kwargs.get("punctuation", True),
                "format_text": kwargs.get("format_text", True),
                "language_code": kwargs.get("language_code", "en_us"),
            }

            # Remove None values
            transcript_data = {
                k: v for k, v in transcript_data.items() if v is not None
            }

            transcript_response = requests.post(
                transcript_url,
                headers=self.headers,
                json=transcript_data,
                timeout=self.timeout,
            )
            transcript_response.raise_for_status()
            transcript_id = transcript_response.json()["id"]

            # Poll for completion
            transcript = self._poll_transcription(transcript_id)
            return transcript.get("text", "")

        except Exception as e:
            logger.error(f"AssemblyAI transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {str(e)}")

    def transcribe_audio_url(self, audio_url: str, **kwargs) -> str:
        """
        Transcribe audio from URL using AssemblyAI direct API calls

        Args:
            audio_url: URL to audio file
            **kwargs: Additional transcription parameters

        Returns:
            Transcribed text

        Raises:
            RuntimeError: If transcription fails
        """
        if not self.api_key:
            raise ValueError(
                "AssemblyAI API key not found. Set assemblyai_authorization environment variable."
            )

        try:
            # Start transcription directly from URL
            transcript_url = f"{self.base_url}/transcript"
            transcript_data = {
                "audio_url": audio_url,
                "language_detection": kwargs.get("language_detection", True),
                "punctuation": kwargs.get("punctuation", True),
                "format_text": kwargs.get("format_text", True),
                "language_code": kwargs.get("language_code", "en_us"),
            }

            # Remove None values
            transcript_data = {
                k: v for k, v in transcript_data.items() if v is not None
            }

            transcript_response = requests.post(
                transcript_url,
                headers=self.headers,
                json=transcript_data,
                timeout=self.timeout,
            )
            transcript_response.raise_for_status()
            transcript_id = transcript_response.json()["id"]

            # Poll for completion
            transcript = self._poll_transcription(transcript_id)
            return transcript.get("text", "")

        except Exception as e:
            logger.error(f"AssemblyAI transcription failed: {e}")
            raise RuntimeError(f"Transcription failed: {str(e)}")

    def _upload_audio_file(self, audio_file_path: str) -> str:
        """Upload audio file to AssemblyAI and return upload URL"""
        upload_url = f"{self.base_url}/upload"

        with open(audio_file_path, "rb") as audio_file:
            response = requests.post(
                upload_url,
                headers={"authorization": self.api_key},
                files={"file": audio_file},
                timeout=self.timeout,
            )

        response.raise_for_status()
        return response.json()["upload_url"]

    def _start_transcription(self, audio_url: str, **kwargs) -> str:
        """Start transcription job and return transcript ID"""
        transcript_url = f"{self.base_url}/transcript"

        # Default transcription parameters
        data = {
            "audio_url": audio_url,
            "language_detection": kwargs.get("language_detection", True),
            "punctuation": kwargs.get("punctuation", True),
            "format_text": kwargs.get("format_text", True),
            "speaker_labels": kwargs.get("speaker_labels", False),
            "auto_highlights": kwargs.get("auto_highlights", False),
            "sentiment_analysis": kwargs.get("sentiment_analysis", False),
            "entity_detection": kwargs.get("entity_detection", False),
            "iab_categories": kwargs.get("iab_categories", False),
            "content_safety_labels": kwargs.get("content_safety_labels", False),
            "auto_chapters": kwargs.get("auto_chapters", False),
            "summarization": kwargs.get("summarization", False),
            "summary_type": kwargs.get("summary_type", "bullets"),
            "summary_model": kwargs.get("summary_model", "informative"),
            "custom_spelling": kwargs.get("custom_spelling", {}),
            "disfluencies": kwargs.get("disfluencies", False),
            "filler_words": kwargs.get("filler_words", False),
            "language_code": kwargs.get("language_code", "en_us"),
            "boost_param": kwargs.get("boost_param", "default"),
            "redact_pii": kwargs.get("redact_pii", False),
            "redact_pii_audio": kwargs.get("redact_pii_audio", False),
            "redact_pii_audio_quality": kwargs.get("redact_pii_audio_quality", "mp3"),
            "redact_pii_policies": kwargs.get("redact_pii_policies", []),
            "webhook_url": kwargs.get("webhook_url"),
            "webhook_auth": kwargs.get("webhook_auth", False),
            "webhook_auth_header_name": kwargs.get(
                "webhook_auth_header_name", "authorization"
            ),
            "filter_profanity": kwargs.get("filter_profanity", False),
            "dual_channel": kwargs.get("dual_channel", False),
            "speech_model": kwargs.get("speech_model", "best"),
            "audio_start_from": kwargs.get("audio_start_from"),
            "audio_end_at": kwargs.get("audio_end_at"),
            "word_boost": kwargs.get("word_boost", []),
            "buzzwords": kwargs.get("buzzwords", False),
            "temperature": kwargs.get("temperature"),
            "language_detection_confidence": kwargs.get(
                "language_detection_confidence"
            ),
            "channels": kwargs.get("channels"),
            "speech_channel_count": kwargs.get("speech_channel_count"),
            "speech_start_from": kwargs.get("speech_start_from"),
            "speech_end_at": kwargs.get("speech_end_at"),
            "speech_threshold": kwargs.get("speech_threshold"),
            "speech_speaker_count": kwargs.get("speech_speaker_count"),
            "speech_speaker_change_sensitivity": kwargs.get(
                "speech_speaker_change_sensitivity"
            ),
            "speech_speaker_labels": kwargs.get("speech_speaker_labels", False),
            "speech_speaker_diarization": kwargs.get(
                "speech_speaker_diarization", False
            ),
            "speech_speaker_diarization_confidence": kwargs.get(
                "speech_speaker_diarization_confidence"
            ),
            "speech_speaker_diarization_speaker_count": kwargs.get(
                "speech_speaker_diarization_speaker_count"
            ),
            "speech_speaker_diarization_speaker_change_sensitivity": kwargs.get(
                "speech_speaker_diarization_speaker_change_sensitivity"
            ),
            "speech_speaker_diarization_speaker_labels": kwargs.get(
                "speech_speaker_diarization_speaker_labels", False
            ),
            "speech_speaker_diarization_speaker_diarization": kwargs.get(
                "speech_speaker_diarization_speaker_diarization", False
            ),
            "speech_speaker_diarization_speaker_diarization_confidence": kwargs.get(
                "speech_speaker_diarization_speaker_diarization_confidence"
            ),
            "speech_speaker_diarization_speaker_diarization_speaker_count": kwargs.get(
                "speech_speaker_diarization_speaker_diarization_speaker_count"
            ),
            "speech_speaker_diarization_speaker_diarization_speaker_change_sensitivity": kwargs.get(
                "speech_speaker_diarization_speaker_diarization_speaker_change_sensitivity"
            ),
            "speech_speaker_diarization_speaker_diarization_speaker_labels": kwargs.get(
                "speech_speaker_diarization_speaker_diarization_speaker_labels", False
            ),
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        response = requests.post(
            transcript_url, headers=self.headers, json=data, timeout=self.timeout
        )

        response.raise_for_status()
        return response.json()["id"]

    def _poll_transcription(self, transcript_id: str) -> Dict[str, Any]:
        """Poll transcription status until completion"""
        transcript_url = f"{self.base_url}/transcript/{transcript_id}"

        for attempt in range(self.max_retries):
            response = requests.get(
                transcript_url, headers=self.headers, timeout=self.timeout
            )
            response.raise_for_status()

            transcript = response.json()
            status = transcript.get("status")

            if status == "completed":
                logger.info(f"Transcription completed: {transcript_id}")
                return transcript
            elif status == "error":
                error_msg = transcript.get("error", "Unknown error")
                raise RuntimeError(f"Transcription failed: {error_msg}")
            elif status in ["processing", "queued"]:
                logger.info(f"Transcription {status}: {transcript_id}")
                time.sleep(self.polling_interval)
            else:
                logger.warning(f"Unknown transcription status: {status}")
                time.sleep(self.polling_interval)

        raise RuntimeError(f"Transcription timeout after {self.max_retries} attempts")

    def get_transcript_info(self, transcript_id: str) -> Dict[str, Any]:
        """Get detailed information about a transcript"""
        transcript_url = f"{self.base_url}/transcript/{transcript_id}"

        response = requests.get(
            transcript_url, headers=self.headers, timeout=self.timeout
        )
        response.raise_for_status()

        return response.json()

    def delete_transcript(self, transcript_id: str) -> bool:
        """Delete a transcript from AssemblyAI"""
        transcript_url = f"{self.base_url}/transcript/{transcript_id}"

        response = requests.delete(
            transcript_url, headers=self.headers, timeout=self.timeout
        )
        return response.status_code == 200
