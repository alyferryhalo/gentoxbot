import pandas as pd
from pandas import array
from pandas import DataFrame

import numpy as np
from numpy import zeros, array

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InputFile

from rdkit import Chem, DataStructs
from rdkit.Chem import Draw, Descriptors, AllChem, Lipinski, MolFromSmiles
from rdkit.Chem.Draw import MolToFile, rdMolDraw2D
import rdkit.Chem.AllChem as AllChem

from scopy.ScoTox import Toxfilter

from TOKEN import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    msg_start = "Введи молекулу в формате SMILES"
    await message.reply(msg_start)

@dp.message_handler()
async def generate_molecule(message: types.Message):
    
    smiles = message.text
    mol = Chem.MolFromSmiles(smiles)
   
    if mol is None:
            await bot.send_message(message.from_user.id, "Неверный SMILES. Попробуй снова...")
    else:
    
        HeavyAtomCount = Chem.Lipinski.HeavyAtomCount(mol)
        NumHeteroatoms = Chem.Lipinski.NumHeteroatoms(mol)
        NumAliphaticHeterocycles = Chem.Lipinski.NumAliphaticHeterocycles(mol)
        NumHAcceptors = Chem.Lipinski.NumHAcceptors(mol)
        
        Filter = Toxfilter(mol, detail=True, showSMILES=True)
        filter_result = Filter.Check_Toxicophores()
        if filter_result[0]['Disposed'] == 'Rejected':
            tox_disposed = 1
            answer_tox = 'да'
        else:
            tox_disposed = 0
            answer_tox = 'нет'
        
        toxofores_names = filter_result[0]['MatchedNames']
        
        await bot.send_message(message.from_user.id, f"Тяжёлых атомов: {HeavyAtomCount}\nГетероатомов: {NumHeteroatoms}\nАлифатических гетероциклов: {NumAliphaticHeterocycles}\nАкцепторов водорода: {NumAliphaticHeterocycles}\nЕсть токсофоры: {answer_tox}\nНайдены токсофоры: {toxofores_names}")
                       
        img = Draw.MolToFile(mol, filename=f'{smiles}.png')
        await bot.send_photo(chat_id=message.chat.id, photo=types.InputFile(f"{smiles}.png", 'rb'))
        

 
if __name__ == '__main__':
    executor.start_polling(dp)

