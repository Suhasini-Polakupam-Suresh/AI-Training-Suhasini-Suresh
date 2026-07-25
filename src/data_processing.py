"""
Data Processing Module for Health Insurance AI Assistant
Handles loading, preprocessing, and chunking of health insurance documents
"""

import os
import json
from typing import List, Dict
from pathlib import Path
import re


class HealthInsuranceDataProcessor:
    """Process health insurance documents for RAG system"""
    
    def __init__(self, raw_data_path: str = "data/raw", processed_data_path: str = "data/processed"):
        self.raw_data_path = Path(raw_data_path)
        self.processed_data_path = Path(processed_data_path)
        self.processed_data_path.mkdir(parents=True, exist_ok=True)
        
    def create_sample_data(self):
        """Create sample health insurance documents"""
        self.raw_data_path.mkdir(parents=True, exist_ok=True)
        
        sample_documents = [
            {
                "title": "Understanding Health Insurance Basics",
                "content": """
                Health Insurance Coverage Overview
                
                What is Health Insurance?
                Health insurance is a contract between you and an insurance company. You pay a premium, 
                and the insurance company agrees to pay for certain medical expenses.
                
                Key Terms:
                - Premium: The amount you pay monthly for your insurance policy
                - Deductible: The amount you must pay before insurance starts covering costs
                - Copay: A fixed amount you pay for a covered service
                - Coinsurance: Your share of costs after meeting the deductible (usually a percentage)
                - Out-of-pocket maximum: The most you'll pay during a policy period
                
                Types of Health Insurance Plans:
                1. HMO (Health Maintenance Organization): Requires you to use network providers
                2. PPO (Preferred Provider Organization): More flexibility in choosing providers
                3. EPO (Exclusive Provider Organization): Network-only coverage except emergencies
                4. POS (Point of Service): Combines HMO and PPO features
                """
            },
            {
                "title": "Mental Health Coverage",
                "content": """
                Mental Health and Substance Abuse Coverage
                
                Under the Affordable Care Act, all marketplace plans must cover mental health services.
                
                Covered Services Include:
                - Behavioral health treatment (psychotherapy and counseling)
                - Mental and behavioral health inpatient services
                - Substance abuse treatment
                - Prescription medications for mental health conditions
                
                Coverage Details:
                - Most plans cover therapy sessions with licensed professionals
                - Many plans offer telehealth options for mental health services
                - Preventive screening for depression is covered at no cost
                - Copays and deductibles apply to most mental health services
                
                Finding Providers:
                - Check your insurance network directory
                - Verify coverage before your first appointment
                - Ask about sliding scale fees if cost is a concern
                """
            },
            {
                "title": "Claims Process Guide",
                "content": """
                How to File Health Insurance Claims
                
                Step-by-Step Claims Process:
                
                1. Receive Medical Services
                   - Present your insurance card at the provider's office
                   - Pay any required copay at time of service
                
                2. Provider Files Claim
                   - Usually, healthcare providers file claims directly
                   - Provider sends itemized bill to insurance company
                
                3. Insurance Reviews Claim
                   - Insurance company reviews for coverage and accuracy
                   - Processing typically takes 30-45 days
                
                4. Explanation of Benefits (EOB)
                   - You receive EOB showing what was covered
                   - EOB is not a bill
                
                5. Pay Your Share
                   - You receive a bill for your portion (deductible, copay, coinsurance)
                   - Payment is due to the healthcare provider, not the insurance company
                
                Emergency Room Claims:
                - Emergency services must be covered even if out-of-network
                - Higher copays typically apply ($150-$500)
                - No prior authorization required for true emergencies
                
                Appealing Denied Claims:
                - Review the denial reason in your EOB
                - Contact insurance company within 180 days
                - Request internal review
                - If still denied, request external review
                """
            },
            {
                "title": "Preventive Care Benefits",
                "content": """
                Preventive Care Services
                
                Under the ACA, preventive services are covered at 100% with no copay or deductible.
                
                Covered Preventive Services:
                
                For Adults:
                - Blood pressure screening
                - Cholesterol screening
                - Type 2 diabetes screening
                - Colorectal cancer screening (age 45-75)
                - Immunizations (flu, pneumonia, HPV)
                - Depression screening
                - Obesity screening and counseling
                
                For Women:
                - Well-woman visits
                - Mammograms (age 40+)
                - Cervical cancer screening
                - Prenatal care
                - Contraception and counseling
                
                For Children:
                - Regular well-child visits
                - Immunizations
                - Vision and hearing screening
                - Developmental assessments
                - Behavioral assessments
                
                Important Notes:
                - Services must be in-network for $0 cost
                - Additional services during preventive visit may incur charges
                - Check with your plan for specific coverage details
                """
            },
            {
                "title": "Prescription Drug Coverage",
                "content": """
                Understanding Prescription Drug Benefits
                
                Formulary Tiers:
                Most insurance plans organize drugs into tiers that affect your cost:
                
                Tier 1 - Generic Drugs: Lowest cost ($10-$20 copay)
                Tier 2 - Preferred Brand Drugs: Medium cost ($30-$60 copay)
                Tier 3 - Non-Preferred Brand Drugs: Higher cost ($70-$100 copay)
                Tier 4 - Specialty Drugs: Highest cost (20-33% coinsurance)
                
                Prior Authorization:
                Some medications require approval before insurance will cover them.
                Your doctor must submit clinical justification.
                
                Mail Order Options:
                - 90-day supply often available at reduced cost
                - Convenient for maintenance medications
                - Usually required for specialty drugs
                
                Generic Substitution:
                - Pharmacists may substitute generic versions
                - Generics are equally effective as brand-name drugs
                - Can save 30-80% on prescription costs
                
                Step Therapy:
                - Some plans require trying lower-cost drugs first
                - If ineffective, you can move to more expensive options
                
                Coverage Gaps:
                - Some plans have annual or lifetime limits on specific drugs
                - Check formulary for coverage details
                - Patient assistance programs available for expensive medications
                """
            }
        ]
        
        # Save sample documents
        for i, doc in enumerate(sample_documents):
            file_path = self.raw_data_path / f"document_{i+1}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(doc, f, indent=2)
        
        print(f"✓ Created {len(sample_documents)} sample documents in {self.raw_data_path}")
        
    def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
            chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters between chunks
            
        Returns:
            List of text chunks
        """
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence ending
                for delimiter in ['. ', '.\n', '! ', '? ']:
                    last_delim = text.rfind(delimiter, start, end)
                    if last_delim != -1:
                        end = last_delim + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
            
        return chunks
    
    def process_documents(self) -> List[Dict]:
        """
        Process all documents in raw data directory
        
        Returns:
            List of processed document chunks with metadata
        """
        if not list(self.raw_data_path.glob("*.json")):
            print("No documents found. Creating sample data...")
            self.create_sample_data()
        
        processed_chunks = []
        
        for file_path in self.raw_data_path.glob("*.json"):
            with open(file_path, 'r', encoding='utf-8') as f:
                doc = json.load(f)
            
            # Chunk the content
            chunks = self.chunk_text(doc['content'])
            
            # Add metadata to each chunk
            for i, chunk in enumerate(chunks):
                processed_chunks.append({
                    'text': chunk,
                    'source': doc['title'],
                    'chunk_id': f"{file_path.stem}_chunk_{i}",
                    'metadata': {
                        'title': doc['title'],
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                })
        
        # Save processed data
        output_file = self.processed_data_path / "processed_chunks.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(processed_chunks, f, indent=2)
        
        print(f"✓ Processed {len(processed_chunks)} chunks from {len(list(self.raw_data_path.glob('*.json')))} documents")
        print(f"✓ Saved to {output_file}")
        
        return processed_chunks
    
    def get_statistics(self) -> Dict:
        """Get statistics about processed data"""
        output_file = self.processed_data_path / "processed_chunks.json"
        
        if not output_file.exists():
            return {"error": "No processed data found"}
        
        with open(output_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        stats = {
            'total_chunks': len(chunks),
            'unique_sources': len(set(chunk['source'] for chunk in chunks)),
            'avg_chunk_length': sum(len(chunk['text']) for chunk in chunks) / len(chunks),
            'sources': list(set(chunk['source'] for chunk in chunks))
        }
        
        return stats


def main():
    """Main execution function"""
    print("=" * 60)
    print("Health Insurance Data Processing")
    print("=" * 60)
    
    processor = HealthInsuranceDataProcessor()
    
    # Process documents
    chunks = processor.process_documents()
    
    # Display statistics
    stats = processor.get_statistics()
    print("\nData Statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Unique documents: {stats['unique_sources']}")
    print(f"  Average chunk length: {stats['avg_chunk_length']:.0f} characters")
    print(f"\nDocuments processed:")
    for source in stats['sources']:
        print(f"  - {source}")
    
    print("\n✓ Data processing complete!")


if __name__ == "__main__":
    main()
