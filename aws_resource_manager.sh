name: AWS Resource Manager

on:
  workflow_dispatch:
    inputs:
      resource:
        description: 'Resource type to manage'
        required: true
        type: choice
        options:
          - ec2
          - rds
          - ecr
          - github
      operation:
        description: 'Operation to perform'
        required: true
        type: choice
        options:
          - start
          - stop
          - status
          - list
      region:
        description: 'AWS region'
        required: false
        default: 'us-east-1'
      resource_ids:
        description: 'Resource IDs (space-separated for EC2/RDS, repo name for ECR)'
        required: false
      github_repo:
        description: 'GitHub repo (owner/repo) for runner operations'
        required: false

jobs:
  manage_resources:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_TO_ASSUME }}
          aws-region: ${{ inputs.region }}
      
      - name: Run AWS Resource Manager
        env:
          RESOURCE: ${{ inputs.resource }}
          OPERATION: ${{ inputs.operation }}
          REGION: ${{ inputs.region }}
          RESOURCE_IDS: ${{ inputs.resource_ids }}
          GITHUB_REPO: ${{ inputs.github_repo }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python aws_resource_manager.py \
            --resource "$RESOURCE" \
            --operation "$OPERATION" \
            --region "$REGION" \
            $([ -n "$RESOURCE_IDS" ] && echo "--ids $RESOURCE_IDS") \
            $([ -n "$GITHUB_REPO" ] && echo "--github-repo $GITHUB_REPO") \
            $([ "$RESOURCE" == "github" ] && echo "--github-token $GITHUB_TOKEN") \
            --json-output
      
      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: aws-operation-logs
          path: logs/
          retention-days: 7