import asyncio
import os
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert
from src.hello_api.notes.models import notes

# Override environment for local connection
os.environ['DB_HOST'] = 'localhost'

# Create engine for local connection
DATABASE_URL = (
    f"postgresql+asyncpg://postgres:postgres@localhost:5432/notes_db"
)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def create_sample_notes():
    """Create sample notes for testing."""
    sample_notes = [
        {
            "id": uuid.uuid4(),
            "title": "Voyager Program",
            "body": """
The Voyager program consists of two robotic probes, Voyager 1 and Voyager 2, launched by NASA in 1977. 
The primary mission was to study the outer planets of our solar system.

Voyager 1 was launched on September 5, 1977, and Voyager 2 was launched on August 20, 1977. 
Both spacecraft carried identical scientific instruments including cameras, spectrometers, and magnetometers.

The Golden Record is a phonograph record included aboard both Voyager spacecraft. It contains sounds and images 
selected to portray the diversity of life and culture on Earth. It includes greetings in 55 languages, 
music from different cultures, and natural sounds like thunder and bird songs.

As of 2024, Voyager 1 has traveled over 15 billion miles from Earth and is the most distant human-made object. 
Voyager 2 has traveled over 12 billion miles. Both spacecraft are still operational and sending data back to Earth.

The instruments carried by the Voyager spacecraft include:
- Imaging Science System (ISS) for taking photographs
- Infrared Interferometer Spectrometer (IRIS) for temperature measurements
- Ultraviolet Spectrometer (UVS) for atmospheric composition
- Planetary Radio Astronomy (PRA) for radio emissions
- Photopolarimeter (PPS) for light polarization studies
- Cosmic Ray System (CRS) for cosmic ray detection
- Low Energy Charged Particles (LECP) for particle analysis
- Magnetometer (MAG) for magnetic field measurements
- Plasma Wave System (PWS) for plasma wave detection
            """
        },
        {
            "id": uuid.uuid4(),
            "title": "Chernobyl Disaster",
            "body": """
The Chernobyl disaster was a nuclear accident that occurred on April 26, 1986, at the Chernobyl Nuclear Power Plant 
in Pripyat, Ukraine, then part of the Soviet Union. It is considered the worst nuclear power plant disaster in history.

The disaster was caused by a combination of design flaws in the RBMK reactor and operator errors during a safety test. 
The test was designed to simulate an electrical power outage to test the emergency cooling system.

The immediate effects included the deaths of two workers from the explosion and 28 firefighters and emergency workers 
from acute radiation syndrome within the first few months. The explosion released large amounts of radioactive material 
into the atmosphere, contaminating large areas of Ukraine, Belarus, and Russia.

The environmental impact was severe, with radioactive contamination affecting soil, water, and air quality. 
The exclusion zone around the plant remains uninhabitable to this day. Wildlife in the area has been affected, 
though some species have adapted to the radiation.

Following the disaster, significant safety measures were implemented worldwide, including:
- Improved reactor designs with better safety systems
- Enhanced operator training and safety protocols
- International cooperation on nuclear safety standards
- Development of emergency response procedures
- Stricter regulations for nuclear power plant operation
            """
        },
        {
            "id": uuid.uuid4(),
            "title": "Periodic Table",
            "body": """
The periodic table is a tabular arrangement of chemical elements, organized by their atomic number, electron configuration, 
and recurring chemical properties. It was first created by Russian chemist Dmitri Mendeleev in 1869.

Elements in the periodic table are organized in order of increasing atomic number, which represents the number of protons 
in an atom's nucleus. The table is arranged in rows (periods) and columns (groups or families).

The main groups in the periodic table include:
- Group 1: Alkali metals (Li, Na, K, Rb, Cs, Fr)
- Group 2: Alkaline earth metals (Be, Mg, Ca, Sr, Ba, Ra)
- Groups 3-12: Transition metals
- Group 13: Boron group (B, Al, Ga, In, Tl)
- Group 14: Carbon group (C, Si, Ge, Sn, Pb)
- Group 15: Nitrogen group (N, P, As, Sb, Bi)
- Group 16: Oxygen group (O, S, Se, Te, Po)
- Group 17: Halogens (F, Cl, Br, I, At)
- Group 18: Noble gases (He, Ne, Ar, Kr, Xe, Rn)

The atomic number represents the number of protons in an atom's nucleus and determines the element's identity. 
It also equals the number of electrons in a neutral atom.

Elements in the same group behave similarly because they have the same number of valence electrons, 
which determines their chemical properties. For example, all alkali metals are highly reactive and form +1 ions, 
while all noble gases are inert and rarely form compounds.
            """
        }
    ]
    
    async with async_session() as session:
        for note_data in sample_notes:
            stmt = insert(notes).values(**note_data)
            await session.execute(stmt)
        
        await session.commit()
        print(f"Created {len(sample_notes)} sample notes")

if __name__ == "__main__":
    asyncio.run(create_sample_notes()) 