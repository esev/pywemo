[![PyPI](https://img.shields.io/badge/pypi-${GITHUB_REF_NAME}-green.svg)](https://pypi.org/project/pywemo/${GITHUB_REF_NAME}/)
[![Coverage Status](https://coveralls.io/repos/github/${GITHUB_REPOSITORY}/badge.svg?branch=${GITHUB_REF_NAME})](https://coveralls.io/github/${GITHUB_REPOSITORY}?branch=${GITHUB_REF_NAME})
[![SLSA](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev/)

${BODY}

### Release metadata

<details>

<summary><code>SHA256</code> Checksums</summary>

```
${SHA256SUM}
```

</details>

<details>

<summary>
  How to verify <code>sigstore</code> signatures
</summary>

Visit [sigstore.dev](https://www.sigstore.dev/) to learn more about sigstore
signing and verification.

Certificate identity:

```
https://github.com/${GITHUB_WORKFLOW_REF}
```

Verify with [`sigstore-python`](https://pypi.org/project/sigstore/):

```bash
# Download the release wheel and .sigstore file.
wget https://github.com/${GITHUB_REPOSITORY}/releases/download/${GITHUB_REF_NAME}/pywemo-${GITHUB_REF_NAME}-py3-none-any.whl
wget https://github.com/${GITHUB_REPOSITORY}/releases/download/${GITHUB_REF_NAME}/pywemo-${GITHUB_REF_NAME}-py3-none-any.whl.sigstore

# Install sigstore.
pip install sigstore

# Verify that the wheel was built from this release.
python -m sigstore verify github \
    --bundle pywemo-${GITHUB_REF_NAME}-py3-none-any.whl.sigstore \
    --cert-identity https://github.com/${GITHUB_WORKFLOW_REF} \
    --sha ${GITHUB_SHA} \
    pywemo-${GITHUB_REF_NAME}-py3-none-any.whl
```

</details>

<details>

<summary>
  How to verify <code>SLSA</code> provenance
</summary>

Visit [slsa.dev](https://slsa.dev/) to learn more about generating and
verifying software provenance with SLSA.

SLSA verifier installation instructions can be found at 
[github.com/slsa-framework/slsa-verifier#installation](https://github.com/slsa-framework/slsa-verifier#installation).

```bash
# Download the release wheel and .intoto.jsonl file.
wget https://github.com/${GITHUB_REPOSITORY}/releases/download/${GITHUB_REF_NAME}/pywemo-${GITHUB_REF_NAME}-py3-none-any.whl
wget https://github.com/${GITHUB_REPOSITORY}/releases/download/${GITHUB_REF_NAME}/provenance-pywemo-${GITHUB_REF_NAME}.intoto.jsonl

# Verify that the wheel was built from this release.
slsa-verifier-linux-amd64 verify-artifact \
    --provenance-path provenance-pywemo-${GITHUB_REF_NAME}.intoto.jsonl \
    --source-uri github.com/${GITHUB_REPOSITORY} \
    --source-tag ${GITHUB_REF_NAME} \
    pywemo-${GITHUB_REF_NAME}-py3-none-any.whl
```

</details>